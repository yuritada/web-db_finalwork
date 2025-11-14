'use client';

import { useState, useEffect, use } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { MessageList } from '@/components/channel/MessageList';
import { MessageInput } from '@/components/channel/MessageInput';
import { AddMemberDialog } from '@/components/channel/AddMemberDialog';
import {
  Message,
  ChannelDetail,
  getChannel,
  getChannelMessages,
  sendChannelMessage
} from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { toast } from 'sonner';
import { UserPlus, Users } from 'lucide-react';

export default function ChannelDetailPage({ params }: { params: Promise<{ channel_id: string }> }) {
  const resolvedParams = use(params);
  const router = useRouter();
  const { user } = useAuth();
  const [channel, setChannel] = useState<ChannelDetail | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAddMemberDialogOpen, setIsAddMemberDialogOpen] = useState(false);

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
      const newMessage = await sendChannelMessage(channelId, { content });

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
            <CardTitle className="text-xl">#{channel.name}</CardTitle>
            <div className="flex items-center gap-2">
              {channel.is_private && (
                <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded">
                  🔒 プライベート
                </span>
              )}
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
    </div>
  );
}
