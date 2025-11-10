'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { getWikiPages, createWikiPage, WikiPagePublic } from '@/lib/api';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

export default function WikiListPage() {
  const router = useRouter();
  const [pages, setPages] = useState<WikiPagePublic[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // 新規作成モーダル用
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newContent, setNewContent] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState('');

  // ページ一覧取得
  const fetchPages = async () => {
    try {
      setIsLoading(true);
      setError('');
      const data = await getWikiPages();
      setPages(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message || 'ページの読み込みに失敗しました');
      } else {
        setError('ページの読み込みに失敗しました');
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPages();
  }, []);

  // 新規作成処理
  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateError('');
    setIsCreating(true);

    try {
      if (!newTitle.trim()) {
        setCreateError('タイトルを入力してください');
        setIsCreating(false);
        return;
      }

      const newPage = await createWikiPage({
        title: newTitle.trim(),
        content: newContent.trim() || undefined,
      });

      // 作成成功
      setIsCreateModalOpen(false);
      setNewTitle('');
      setNewContent('');

      // 詳細ページへ遷移
      router.push(`/main/wiki/${newPage.id}`);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setCreateError(err.message || 'ページの作成に失敗しました');
      } else {
        setCreateError('ページの作成に失敗しました');
      }
    } finally {
      setIsCreating(false);
    }
  };

  const handleCloseCreateModal = () => {
    setIsCreateModalOpen(false);
    setNewTitle('');
    setNewContent('');
    setCreateError('');
  };

  // 日時フォーマット
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Wiki</h1>
          <p className="mt-2 text-gray-600">
            知識を共有するためのWikiページを作成・閲覧できます。
          </p>
        </div>

        {/* 新規作成ボタン */}
        <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
          <DialogTrigger asChild>
            <Button>新規作成</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>新しいWikiページを作成</DialogTitle>
              <DialogDescription>
                タイトルと初期コンテンツを入力してください。
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="title" className="text-sm font-medium">
                  タイトル <span className="text-red-500">*</span>
                </label>
                <Input
                  id="title"
                  type="text"
                  placeholder="例: プロジェクト概要"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  disabled={isCreating}
                  required
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="content" className="text-sm font-medium">
                  初期コンテンツ（任意）
                </label>
                <Textarea
                  id="content"
                  placeholder="ここに内容を入力..."
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  disabled={isCreating}
                  rows={6}
                />
              </div>

              {createError && (
                <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
                  {createError}
                </div>
              )}

              <div className="flex justify-end gap-3 pt-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleCloseCreateModal}
                  disabled={isCreating}
                >
                  キャンセル
                </Button>
                <Button type="submit" disabled={isCreating}>
                  {isCreating ? '作成中...' : '作成する'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* エラー表示 */}
      {error && (
        <div className="p-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
          {error}
        </div>
      )}

      {/* ローディング */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-sky-500 border-r-transparent"></div>
            <p className="mt-2 text-sm text-gray-600">読み込み中...</p>
          </div>
        </div>
      )}

      {/* ページ一覧 */}
      {!isLoading && !error && (
        <>
          {pages.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <p className="text-gray-500">まだWikiページがありません。</p>
                  <p className="text-sm text-gray-400 mt-2">
                    「新規作成」ボタンから最初のページを作成してみましょう。
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {pages.map((page) => (
                <Link key={page.id} href={`/main/wiki/${page.id}`}>
                  <Card className="hover:shadow-md transition-shadow cursor-pointer">
                    <CardHeader>
                      <CardTitle className="text-lg">{page.title}</CardTitle>
                      <CardDescription>
                        作成者: {page.creator_id}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {/* コンテンツプレビュー */}
                        {page.content && (
                          <p className="text-sm text-gray-600 line-clamp-2">
                            {page.content}
                          </p>
                        )}

                        {/* メタ情報 */}
                        <div className="flex gap-4 text-xs text-gray-500">
                          <div>
                            作成: {formatDate(page.created_at)}
                          </div>
                          <div>
                            更新: {formatDate(page.updated_at)}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
