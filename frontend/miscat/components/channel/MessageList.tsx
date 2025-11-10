'use client';

import { useEffect, useRef } from 'react';
import { MessageCard } from './MessageCard';
import { Message } from '@/lib/api';

interface MessageListProps {
  messages: Message[];
  currentUserId: string;
  onLoadMore?: () => void;
}

export function MessageList({ messages, currentUserId, onLoadMore }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // 新着メッセージの自動スクロール
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // スクロール上部到達時の処理（将来: 古いメッセージ読み込み）
  const handleScroll = () => {
    if (scrollContainerRef.current && onLoadMore) {
      const { scrollTop } = scrollContainerRef.current;
      if (scrollTop === 0) {
        // スクロール上部に到達
        onLoadMore();
      }
    }
  };

  return (
    <div
      ref={scrollContainerRef}
      onScroll={handleScroll}
      className="flex-1 overflow-y-auto p-4 bg-gray-50 space-y-2"
    >
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full">
          <p className="text-gray-500">まだメッセージがありません</p>
        </div>
      ) : (
        <>
          {messages.map((message) => (
            <MessageCard
              key={message.id}
              message={message}
              isOwnMessage={message.sender_id === currentUserId}
            />
          ))}
          <div ref={messagesEndRef} />
        </>
      )}
    </div>
  );
}
