'use client';

import { useState, useEffect, use, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { MessageList } from '@/components/channel/MessageList';
import { MessageInput } from '@/components/channel/MessageInput';
import { CreateWikiFromMessagesDialog } from '@/components/wiki/CreateWikiFromMessagesDialog';
import { Message, getDMMessages, sendDMMessage, createWikiPage } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { toast } from 'sonner';
import { BookText, Sparkles, Wifi, WifiOff } from 'lucide-react';
import { autoGenerateWikiContent, generateWikiTitle } from '@/lib/wikiGenerator';
import { useWebSocket, WebSocketMessage } from '@/hooks/useWebSocket';

export default function DMDetailPage({ params }: { params: Promise<{ dm_id: string }> }) {
  const resolvedParams = use(params);
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [partnerUsername, setPartnerUsername] = useState('');
  const [isWikiDialogOpen, setIsWikiDialogOpen] = useState(false);

  // dm_idは実際にはpartner_idとして扱う
  const partnerId = resolvedParams.dm_id;

  // WebSocket URL
  const wsBaseUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
  const wsUrl = user ? `${wsBaseUrl}/ws/dm/${partnerId}` : null;

  // WebSocket接続
  const { isConnected, lastMessage, sendMessage: wsSendMessage } = useWebSocket(wsUrl, {
    onMessage: useCallback((message: WebSocketMessage) => {
      if (message.type === 'new_message' && message.message) {
        // 新しいメッセージを受信したら、メッセージリストに追加
        // 自分が送ったメッセージは既にリストにあるので重複チェック
        setMessages(prevMessages => {
          const isDuplicate = prevMessages.some(
            m => m.id === message.message.id ||
            (m.content === message.message.content &&
             m.sender_id === message.message.sender_id &&
             Math.abs(new Date(m.created_at).getTime() - new Date(message.message.created_at).getTime()) < 1000)
          );

          if (isDuplicate) {
            return prevMessages;
          }

          return [...prevMessages, message.message];
        });
      }
    }, []),
    onConnect: () => {
      console.log('WebSocket connected to DM:', partnerId);
    },
    onDisconnect: () => {
      console.log('WebSocket disconnected from DM:', partnerId);
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
    }
  });

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
      // HTTP APIでメッセージを保存
      const newMessage = await sendDMMessage({
        receiver_id: partnerId,
        content,
      });

      // メッセージリストに即座に追加（楽観的更新）
      setMessages([...messages, newMessage]);

      // WebSocketで他の接続にブロードキャスト
      if (isConnected) {
        wsSendMessage({
          type: 'message',
          message: newMessage
        });
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        throw new Error(err.message);
      } else {
        throw new Error('メッセージの送信に失敗しました');
      }
    }
  };

  // 即座に自動生成
  const handleQuickAutoGenerate = async () => {
    if (messages.length === 0) {
      toast.error('メッセージがありません');
      return;
    }

    try {
      const autoContent = autoGenerateWikiContent(messages);
      const autoTitle = generateWikiTitle(messages, `DMの会話: ${partnerUsername || partnerId}`);

      const newPage = await createWikiPage({
        title: autoTitle,
        content: autoContent,
      });

      toast.success('Wikiページを自動生成しました');
      router.push(`/wiki/${newPage.id}`);
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error('Wikiの自動生成に失敗しました: ' + err.message);
      } else {
        toast.error('Wikiの自動生成に失敗しました');
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
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CardTitle className="text-xl">{partnerUsername || partnerId}</CardTitle>
              {/* WebSocket接続状態インジケーター */}
              <div className="flex items-center gap-1.5">
                {isConnected ? (
                  <>
                    <Wifi className="h-4 w-4 text-green-500" />
                    <span className="text-xs text-green-600">リアルタイム</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="h-4 w-4 text-gray-400" />
                    <span className="text-xs text-gray-500">オフライン</span>
                  </>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => setIsWikiDialogOpen(true)}
                disabled={messages.length === 0}
              >
                <BookText className="h-4 w-4 mr-2" />
                Wikiにまとめる
              </Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={handleQuickAutoGenerate}
                disabled={messages.length === 0}
              >
                <Sparkles className="h-4 w-4 mr-2" />
                自動生成
              </Button>
            </div>
          </div>
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

      {/* Wikiにまとめるダイアログ */}
      <CreateWikiFromMessagesDialog
        open={isWikiDialogOpen}
        onOpenChange={setIsWikiDialogOpen}
        messages={messages}
        defaultTitle={`DMの会話: ${partnerUsername || partnerId}`}
      />
    </div>
  );
}
