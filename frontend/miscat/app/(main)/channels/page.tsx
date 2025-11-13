'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { ChannelCard } from '@/components/channel/ChannelCard';
import { ChannelPublic, getChannels, createChannel } from '@/lib/api';
import { toast } from 'sonner';

export default function ChannelsPage() {
  const router = useRouter();
  const [channels, setChannels] = useState<ChannelPublic[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newChannelName, setNewChannelName] = useState('');
  const [newChannelDescription, setNewChannelDescription] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  // チャンネル一覧取得
  const fetchChannels = async () => {
    try {
      setIsLoading(true);
      const data = await getChannels();
      setChannels(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error('チャンネルの読み込みに失敗しました: ' + err.message);
      } else {
        toast.error('チャンネルの読み込みに失敗しました');
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchChannels();
  }, []);

  // チャンネル作成
  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!newChannelName.trim()) {
      toast.error('チャンネル名を入力してください');
      return;
    }

    setIsCreating(true);

    try {
      await createChannel({
        name: newChannelName.trim(),
        description: newChannelDescription.trim() || undefined
      });
      toast.success('チャンネルを作成しました');
      setIsCreateModalOpen(false);
      setNewChannelName('');
      setNewChannelDescription('');
      fetchChannels(); // 一覧を再取得
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error('チャンネルの作成に失敗しました: ' + err.message);
      } else {
        toast.error('チャンネルの作成に失敗しました');
      }
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">チャンネル</h1>
          <p className="mt-2 text-gray-600">
            テーマ別のチャンネルでメッセージを共有できます
          </p>
        </div>

        {/* 新規作成ボタン */}
        <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
          <DialogTrigger asChild>
            <Button>新規作成</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>新しいチャンネルを作成</DialogTitle>
              <DialogDescription>
                チャンネル名と説明を入力してください。
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="channelName" className="text-sm font-medium">
                  チャンネル名 <span className="text-red-500">*</span>
                </label>
                <Input
                  id="channelName"
                  type="text"
                  placeholder="例: プロジェクトA"
                  value={newChannelName}
                  onChange={(e) => setNewChannelName(e.target.value)}
                  required
                  maxLength={100}
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="channelDescription" className="text-sm font-medium">
                  説明（任意）
                </label>
                <textarea
                  id="channelDescription"
                  placeholder="チャンネルの説明を入力"
                  value={newChannelDescription}
                  onChange={(e) => setNewChannelDescription(e.target.value)}
                  className="w-full min-h-[100px] px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500"
                  maxLength={500}
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setIsCreateModalOpen(false);
                    setNewChannelName('');
                    setNewChannelDescription('');
                  }}
                >
                  キャンセル
                </Button>
                <Button type="submit">
                  作成する
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* チャンネル一覧 */}
      {channels.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <p className="text-gray-500">まだチャンネルがありません。</p>
              <p className="text-sm text-gray-400 mt-2">
                「新規作成」ボタンから最初のチャンネルを作成してみましょう。
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {channels.map((channel) => (
            <ChannelCard
              key={channel.id}
              channel={channel}
              onClick={() => router.push(`/channels/${channel.id}`)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
