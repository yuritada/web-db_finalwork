import { useEffect, useRef, useState, useCallback } from 'react';
import { getAuthToken } from '@/lib/api';

export interface WebSocketMessage {
  type: 'connection' | 'new_message' | 'pong' | 'error';
  status?: string;
  channel_id?: number;
  partner_id?: string;
  user_id?: string;
  username?: string;
  message?: any;
  sender_id?: string;
  sender_username?: string;
}

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: (code?: number, reason?: string) => void;
  onError?: (error: Event) => void;
  onAuthError?: () => void;  // 認証エラー時のコールバック
}

/**
 * WebSocket接続を管理するカスタムフック
 *
 * @param url WebSocketのURL（例: ws://localhost:8000/ws/channels/1）
 * @param options コールバック関数などのオプション
 * @returns WebSocketの状態と送信関数
 */
export function useWebSocket(url: string | null, options: UseWebSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const isConnectingRef = useRef(false); // Prevent duplicate connection attempts
  const optionsRef = useRef(options); // Store options in ref to prevent reconnection on options change
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  // Update options ref when options change
  useEffect(() => {
    optionsRef.current = options;
  }, [options]);

  // 最大再接続試行回数
  const MAX_RECONNECT_ATTEMPTS = 5;
  // 再接続間隔（ミリ秒）
  const RECONNECT_INTERVAL = 3000;
  // Ping送信間隔（ミリ秒）
  const PING_INTERVAL = 30000;

  /**
   * WebSocketメッセージを送信
   */
  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Message not sent:', message);
    }
  }, []);

  /**
   * Pingを送信して接続を維持
   */
  const sendPing = useCallback(() => {
    sendMessage({ type: 'ping' });
  }, [sendMessage]);

  /**
   * WebSocket接続を確立
   */
  const connect = useCallback(() => {
    if (!url) {
      console.log('[useWebSocket] No URL provided, skipping connect');
      return;
    }

    // 既に接続中または接続済みの場合はスキップ
    if (isConnectingRef.current) {
      console.log('[useWebSocket] Already connecting, skipping...');
      return;
    }

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      console.log('[useWebSocket] Already connected (OPEN state), skipping...');
      return;
    }

    console.log('[useWebSocket] Starting new connection to:', url);
    isConnectingRef.current = true;

    // 既存の接続をクリーンアップ
    if (wsRef.current) {
      wsRef.current.close();
    }

    // トークンを取得
    const token = getAuthToken();
    if (!token) {
      console.error('No authentication token found');
      optionsRef.current.onError?.(new Event('No authentication token'));
      return;
    }

    // WebSocket URLにトークンを追加
    const wsUrl = `${url}?token=${token}`;

    try {
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected:', url);
        isConnectingRef.current = false;
        setIsConnected(true);
        setReconnectAttempts(0);
        optionsRef.current.onConnect?.();

        // Ping送信を開始
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }
        pingIntervalRef.current = setInterval(sendPing, PING_INTERVAL);
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
          optionsRef.current.onMessage?.(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        isConnectingRef.current = false;
        optionsRef.current.onError?.(error);
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        isConnectingRef.current = false;
        setIsConnected(false);
        optionsRef.current.onDisconnect?.(event.code, event.reason);

        // Ping送信を停止
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        // クローズコードに応じた処理
        if (event.code === 4001) {
          // 認証エラー (4001) - 再接続せずに認証エラーコールバックを呼ぶ
          console.error('Authentication failed. Token may be invalid or expired.');
          optionsRef.current.onAuthError?.();
          return; // 再接続しない
        }

        // サーバー再起動 (1012) やその他の切断 - 自動再接続を試みる
        if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS && url) {
          const isServerRestart = event.code === 1012;
          if (isServerRestart) {
            console.log('Server restarting, will reconnect automatically...');
          }

          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`Reconnecting... (attempt ${reconnectAttempts + 1}/${MAX_RECONNECT_ATTEMPTS})`);
            setReconnectAttempts(prev => prev + 1);
            connect();
          }, RECONNECT_INTERVAL);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      isConnectingRef.current = false;
      optionsRef.current.onError?.(new Event('Connection failed'));
    }
  }, [url, reconnectAttempts, sendPing]);

  /**
   * WebSocket接続をクリーンアップ
   */
  const disconnect = useCallback(() => {
    isConnectingRef.current = false;

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
  }, []);

  /**
   * URLが変更されたら接続
   */
  useEffect(() => {
    if (url) {
      console.log('[useWebSocket useEffect] URL changed, connecting...', url);
      connect();
    }

    return () => {
      console.log('[useWebSocket useEffect] Cleanup - disconnecting');
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url]); // connectとdisconnectは依存配列から除外（無限ループ防止）

  return {
    isConnected,
    lastMessage,
    sendMessage,
    disconnect,
    reconnect: connect,
  };
}
