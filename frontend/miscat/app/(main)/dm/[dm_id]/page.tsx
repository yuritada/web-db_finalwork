'use client';

import { useState, useEffect, use } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { MessageList } from '@/components/channel/MessageList';
import { MessageInput } from '@/components/channel/MessageInput';
import { Message, getDMMessages, sendDMMessage } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { toast } from 'sonner';

export default function DMDetailPage({ params }: { params: Promise<{ dm_id: string }> }) {
  const resolvedParams = use(params);
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [partnerUsername, setPartnerUsername] = useState('');

  // dm_idは実際にはpartner_idとして扱う
  const partnerId = resolvedParams.dm_id;

  // URLパラメータからユーザー名を取得
  const usernameFromUrl = searchParams.get('username');

  // メッセージ履歴取得
  const fetchMessages = async () => {
    try {
      setIsLoading(true);
      const data = await getDMMessages(partnerId);
      setMessages(data);

      // パートナーのユーザー名を設定
      // 優先順位: URLパラメータ > メッセージから推測
      if (usernameFromUrl) {
        setPartnerUsername(usernameFromUrl);
      } else if (data.length > 0) {
        const partnerMessage = data.find(m => m.sender_id === partnerId);
        if (partnerMessage) {
          setPartnerUsername(partnerMessage.sender_username);
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error('メッセージの読み込みに失敗しました: ' + err.message);
      } else {
        toast.error('メッセージの読み込みに失敗しました');
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMessages();
  }, [partnerId]); // eslint-disable-line react-hooks/exhaustive-deps

  // メッセージ送信
  const handleSendMessage = async (content: string) => {
    try {
      const newMessage = await sendDMMessage({
        receiver_id: partnerId,
        content,
      });

      // メッセージリストに追加
      setMessages([...messages, newMessage]);
    } catch (err: unknown) {
      if (err instanceof Error) {
        throw new Error(err.message);
      } else {
        throw new Error('メッセージの送信に失敗しました');
      }
    }
  };

  // ローディング中
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-sky-500 border-r-transparent"></div>
          <p className="mt-2 text-sm text-gray-600">読み込み中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* パンくず */}
      <div className="text-sm text-gray-600">
        <button onClick={() => router.push('/dm')} className="hover:underline">
          DM
        </button>
        <span className="mx-2">/</span>
        <span className="text-gray-900">
          {partnerUsername || partnerId}との会話
        </span>
      </div>

      {/* 相手情報 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">{partnerUsername || partnerId}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">ユーザーID:</span>
            <span className="text-xs text-gray-700">{partnerId}</span>
          </div>
        </CardContent>
      </Card>

      {/* メッセージエリア */}
      <div className="bg-white rounded-lg shadow-sm flex flex-col" style={{ height: 'calc(100vh - 400px)' }}>
        <MessageList
          messages={messages}
          currentUserId={user?.id || ''}
        />
        <MessageInput onSend={handleSendMessage} />
      </div>
    </div>
  );
}
