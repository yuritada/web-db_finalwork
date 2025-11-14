'use client';

import { useState, useEffect, use, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { MessageList } from '@/components/channel/MessageList';
import { MessageInput } from '@/components/channel/MessageInput';
import { AddMemberDialog } from '@/components/channel/AddMemberDialog';
import { CreateWikiFromMessagesDialog } from '@/components/wiki/CreateWikiFromMessagesDialog';
import {
  Message,
  ChannelDetail,
  getChannel,
  getChannelMessages,
  sendChannelMessage,
  createWikiPage
} from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { toast } from 'sonner';
import { UserPlus, Users, BookText, Sparkles, Wifi, WifiOff } from 'lucide-react';
import { autoGenerateWikiContent, generateWikiTitle } from '@/lib/wikiGenerator';
import { useWebSocket, WebSocketMessage } from '@/hooks/useWebSocket';

export default function ChannelDetailPage({ params }: { params: Promise<{ channel_id: string }> }) {
  const resolvedParams = use(params);
  const router = useRouter();
  const { user } = useAuth();
  const [channel, setChannel] = useState<ChannelDetail | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAddMemberDialogOpen, setIsAddMemberDialogOpen] = useState(false);
  const [isWikiDialogOpen, setIsWikiDialogOpen] = useState(false);

  // WebSocket URL（backendコンテナ内ではbackend:8000、ブラウザからはlocalhost:8000）
  const wsBaseUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
  const channelId = parseInt(resolvedParams.channel_id);
  const wsUrl = user ? `${wsBaseUrl}/ws/channels/${channelId}` : null;

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
      console.log('WebSocket connected to channel:', channelId);
    },
    onDisconnect: () => {
      console.log('WebSocket disconnected from channel:', channelId);
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
    }
  });

  // チャンネル情報とメッセージ取得
  const fetchData = async () => {
    try {
      setIsLoading(true);
      const channelId = parseInt(resolvedParams.channel_id);

      // チャンネル情報取得
      const channelData = await getChannel(channelId);
      setChannel(channelData);

      // メッセージ取得
      const messagesData = await getChannelMessages(channelId);
      setMessages(messagesData);
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error('データの読み込みに失敗しました: ' + err.message);
      } else {
        toast.error('データの読み込みに失敗しました');
      }
      // エラー時は一覧に戻る
      router.push('/channels');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [resolvedParams.channel_id]); // eslint-disable-line react-hooks/exhaustive-deps

  // メッセージ送信
  const handleSendMessage = async (content: string) => {
    if (!channel) return;

    try {
      const channelId = parseInt(resolvedParams.channel_id);
      // HTTP APIでメッセージを保存
      const newMessage = await sendChannelMessage(channelId, { content });

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
      const autoTitle = generateWikiTitle(messages, `チャンネル: ${channel?.name || ''}`);

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

  // チャンネル情報がない場合
  if (!channel) {
    return null;
  }

  return (
    <div className="space-y-4">
      {/* パンくず */}
      <div className="text-sm text-gray-600">
        <button onClick={() => router.push('/channels')} className="hover:underline">
          チャンネル
        </button>
        <span className="mx-2">/</span>
        <span className="text-gray-900">#{channel.name}</span>
      </div>

      {/* チャンネル情報 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CardTitle className="text-xl">#{channel.name}</CardTitle>
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
              {channel.is_private && (
                <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded">
                  🔒 プライベート
                </span>
              )}
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
              <Button
                size="sm"
                onClick={() => setIsAddMemberDialogOpen(true)}
              >
                <UserPlus className="h-4 w-4 mr-2" />
                メンバー追加
              </Button>
            </div>
          </div>
          {channel.description && (
            <p className="text-sm text-gray-600 mt-2">{channel.description}</p>
          )}
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p className="text-xs text-gray-500">
              チャンネルID: {channel.id}
            </p>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Users className="h-4 w-4" />
              <span>{channel.member_count} メンバー</span>
            </div>
            {channel.members && channel.members.length > 0 && (
              <div className="mt-3">
                <p className="text-xs font-medium text-gray-700 mb-2">メンバー一覧:</p>
                <div className="flex flex-wrap gap-2">
                  {channel.members.map((member) => (
                    <span
                      key={member.id}
                      className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                    >
                      {member.username}
                    </span>
                  ))}
                </div>
              </div>
            )}
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

      {/* メンバー追加ダイアログ */}
      <AddMemberDialog
        open={isAddMemberDialogOpen}
        onOpenChange={setIsAddMemberDialogOpen}
        channelId={parseInt(resolvedParams.channel_id)}
        onMemberAdded={fetchData}
      />

      {/* Wikiにまとめるダイアログ */}
      <CreateWikiFromMessagesDialog
        open={isWikiDialogOpen}
        onOpenChange={setIsWikiDialogOpen}
        messages={messages}
        defaultTitle={`チャンネル: ${channel.name}`}
      />
    </div>
  );
}
