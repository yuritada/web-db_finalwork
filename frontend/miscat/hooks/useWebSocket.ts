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
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
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
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

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
    if (!url) return;

    // 既存の接続をクリーンアップ
    if (wsRef.current) {
      wsRef.current.close();
    }

    // トークンを取得
    const token = getAuthToken();
    if (!token) {
      console.error('No authentication token found');
      options.onError?.(new Event('No authentication token'));
      return;
    }

    // WebSocket URLにトークンを追加
    const wsUrl = `${url}?token=${token}`;

    try {
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected:', url);
        setIsConnected(true);
        setReconnectAttempts(0);
        options.onConnect?.();

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
          options.onMessage?.(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        options.onError?.(error);
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        options.onDisconnect?.();

        // Ping送信を停止
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        // 自動再接続（最大試行回数まで）
        if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS && url) {
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
      options.onError?.(new Event('Connection failed'));
    }
  }, [url, options, reconnectAttempts, sendPing]);

  /**
   * WebSocket接続をクリーンアップ
   */
  const disconnect = useCallback(() => {
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
      connect();
    }

    return () => {
      disconnect();
    };
  }, [url]); // connectとdisconnectは依存配列から除外（無限ループ防止）

  return {
    isConnected,
    lastMessage,
    sendMessage,
    disconnect,
    reconnect: connect,
  };
}
