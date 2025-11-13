'use client';

import React, { createContext, useContext, useEffect, useState, useRef, ReactNode } from 'react';

interface WebSocketContextType {
  socket: WebSocket | null;
  isConnected: boolean;
  sendMessage: (message: unknown) => void;
  subscribe: (channelId: number | string) => void;
  unsubscribe: (channelId: number | string) => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

interface WebSocketProviderProps {
  children: ReactNode;
}

export function WebSocketProvider({ children }: WebSocketProviderProps) {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 3000; // 3 seconds

  const connect = () => {
    try {
      // WebSocket接続先（環境変数から取得、デフォルトはlocalhost）
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('[WebSocket] Connected');
        setIsConnected(true);
        reconnectAttemptsRef.current = 0; // リセット
      };

      ws.onclose = () => {
        console.log('[WebSocket] Disconnected');
        setIsConnected(false);
        setSocket(null);

        // 自動再接続ロジック
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          console.log(`[WebSocket] Reconnecting... (${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectDelay);
        } else {
          console.error('[WebSocket] Max reconnect attempts reached');
        }
      };

      ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error);
      };

      setSocket(ws);
    } catch (error) {
      console.error('[WebSocket] Connection failed:', error);
    }
  };

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (socket) {
        socket.close();
      }
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const sendMessage = (message: unknown) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message));
    } else {
      console.warn('[WebSocket] Cannot send message: not connected');
    }
  };

  const subscribe = (channelId: number | string) => {
    sendMessage({ type: 'subscribe', channel_id: channelId });
  };

  const unsubscribe = (channelId: number | string) => {
    sendMessage({ type: 'unsubscribe', channel_id: channelId });
  };

  return (
    <WebSocketContext.Provider value={{ socket, isConnected, sendMessage, subscribe, unsubscribe }}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
}
