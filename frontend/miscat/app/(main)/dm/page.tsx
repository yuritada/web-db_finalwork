'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/card';
import { DMCard } from '@/components/dm/DMCard';
import { DMConversation, getDMConversations } from '@/lib/api';
import { toast } from 'sonner';

export default function DMPage() {
  const router = useRouter();
  const [conversations, setConversations] = useState<DMConversation[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // DM会話一覧取得
  const fetchConversations = async () => {
    try {
      setIsLoading(true);
      const data = await getDMConversations();
      setConversations(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error('DM一覧の読み込みに失敗しました: ' + err.message);
      } else {
        toast.error('DM一覧の読み込みに失敗しました');
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

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
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">ダイレクトメッセージ</h1>
          <p className="mt-2 text-gray-600">
            他のユーザーと1対1でメッセージを送受信できます
          </p>
        </div>
      </div>

      {/* DM一覧 */}
      {conversations.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <p className="text-gray-500">まだDMがありません。</p>
              <p className="text-sm text-gray-400 mt-2">
                ユーザー検索からメッセージを送信してDMを開始できます。
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {conversations.map((dm) => (
            <DMCard
              key={dm.partner_id}
              dm={dm}
              onClick={() => router.push(`/main/dm/${dm.partner_id}`)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
