'use client';

import { useState, KeyboardEvent } from 'react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

interface MessageInputProps {
  onSend: (content: string) => Promise<void>;
  placeholder?: string;
  maxLength?: number;
}

export function MessageInput({
  onSend,
  placeholder = 'メッセージを入力',
  maxLength = 1000,
}: MessageInputProps) {
  const [content, setContent] = useState('');
  const [isSending, setIsSending] = useState(false);

  const handleSend = async () => {
    const trimmedContent = content.trim();

    if (!trimmedContent) {
      toast.error('メッセージを入力してください');
      return;
    }

    if (trimmedContent.length > maxLength) {
      toast.error(`メッセージは${maxLength}文字以内で入力してください`);
      return;
    }

    setIsSending(true);

    try {
      await onSend(trimmedContent);
      setContent(''); // 送信成功後、入力欄をクリア
      toast.success('メッセージを送信しました');
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error('メッセージの送信に失敗しました: ' + err.message);
      } else {
        toast.error('メッセージの送信に失敗しました');
      }
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Enterキーで送信（Shift+Enterで改行）
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-200 p-4 bg-white">
      <div className="flex gap-2">
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="flex-1 min-h-[80px] max-h-[200px] px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent resize-none"
          disabled={isSending}
          maxLength={maxLength}
        />
        <Button onClick={handleSend} disabled={isSending || !content.trim()} className="self-end">
          {isSending ? '送信中...' : '送信'}
        </Button>
      </div>
      <p className="text-xs text-gray-500 mt-1">
        {content.length}/{maxLength}文字 | Enterで送信、Shift+Enterで改行
      </p>
    </div>
  );
}
