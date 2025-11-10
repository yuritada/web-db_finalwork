'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { getTags, createTag, assignTag, deleteTag, TagPublic } from '@/lib/api';
import { toast } from 'sonner';
import { useAuth } from '@/context/AuthContext';

export default function TagsPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [tags, setTags] = useState<TagPublic[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // 新規作成モーダル
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newTagName, setNewTagName] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  // 割り当てモーダル
  const [assignModalTag, setAssignModalTag] = useState<TagPublic | null>(null);
  const [assignUserId, setAssignUserId] = useState('');
  const [isAssigning, setIsAssigning] = useState(false);

  // 削除確認モーダル
  const [deleteModalTag, setDeleteModalTag] = useState<TagPublic | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // タグ一覧取得
  const fetchTags = async () => {
    try {
      setIsLoading(true);
      const data = await getTags();
      setTags(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error('タグの読み込みに失敗しました: ' + err.message);
      } else {
        toast.error('タグの読み込みに失敗しました');
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTags();
  }, []);

  // タグ作成
  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!newTagName.trim()) {
      toast.error('タグ名を入力してください');
      return;
    }

    setIsCreating(true);

    try {
      await createTag({ name: newTagName.trim() });
      toast.success('タグを作成しました');
      setIsCreateModalOpen(false);
      setNewTagName('');
      fetchTags(); // 一覧を再取得
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error('タグの作成に失敗しました: ' + err.message);
      } else {
        toast.error('タグの作成に失敗しました');
      }
    } finally {
      setIsCreating(false);
    }
  };

  // タグ割り当て
  const handleAssign = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!assignModalTag) return;

    if (!assignUserId.trim()) {
      toast.error('ユーザーIDを入力してください');
      return;
    }

    setIsAssigning(true);

    try {
      await assignTag(assignModalTag.id, assignUserId.trim());
      toast.success('タグを割り当てました');
      setAssignModalTag(null);
      setAssignUserId('');
      fetchTags(); // 一覧を再取得
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error('タグの割り当てに失敗しました: ' + err.message);
      } else {
        toast.error('タグの割り当てに失敗しました');
      }
    } finally {
      setIsAssigning(false);
    }
  };

  // タグ削除
  const handleDelete = async () => {
    if (!deleteModalTag) return;

    setIsDeleting(true);

    try {
      await deleteTag(deleteModalTag.id);
      toast.success('タグを削除しました');
      setDeleteModalTag(null);
      fetchTags(); // 一覧を再取得
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error('タグの削除に失敗しました: ' + err.message);
      } else {
        toast.error('タグの削除に失敗しました');
      }
    } finally {
      setIsDeleting(false);
    }
  };

  // 作成者かどうか判定
  const isCreator = (tag: TagPublic) => {
    return user?.id === tag.creator_id;
  };

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">タグ管理</h1>
          <p className="mt-2 text-gray-600">
            タグを作成・管理して、ユーザーに割り当てることができます。
          </p>
        </div>

        {/* 新規作成ボタン */}
        <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
          <DialogTrigger asChild>
            <Button>新規作成</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>新しいタグを作成</DialogTitle>
              <DialogDescription>
                タグ名を入力してください。
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="tagName" className="text-sm font-medium">
                  タグ名 <span className="text-red-500">*</span>
                </label>
                <Input
                  id="tagName"
                  type="text"
                  placeholder="例: React"
                  value={newTagName}
                  onChange={(e) => setNewTagName(e.target.value)}
                  disabled={isCreating}
                  required
                  maxLength={100}
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setIsCreateModalOpen(false);
                    setNewTagName('');
                  }}
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

      {/* ローディング */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-sky-500 border-r-transparent"></div>
            <p className="mt-2 text-sm text-gray-600">読み込み中...</p>
          </div>
        </div>
      )}

      {/* タグ一覧 */}
      {!isLoading && (
        <>
          {tags.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <p className="text-gray-500">まだタグがありません。</p>
                  <p className="text-sm text-gray-400 mt-2">
                    「新規作成」ボタンから最初のタグを作成してみましょう。
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {tags.map((tag) => (
                <Card key={tag.id}>
                  <CardHeader>
                    <CardTitle className="text-lg">{tag.name}</CardTitle>
                    <CardDescription>
                      作成者: {tag.creator_id}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex gap-2">
                      {/* 詳細ボタン */}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => router.push(`/main/tags/${tag.id}`)}
                        className="flex-1"
                      >
                        詳細
                      </Button>

                      {/* 割り当てボタン */}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setAssignModalTag(tag)}
                        className="flex-1"
                      >
                        割り当て
                      </Button>

                      {/* 削除ボタン（作成者のみ） */}
                      {isCreator(tag) && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setDeleteModalTag(tag)}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          削除
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </>
      )}

      {/* 割り当てモーダル */}
      <Dialog open={!!assignModalTag} onOpenChange={(open) => !open && setAssignModalTag(null)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>タグを割り当て</DialogTitle>
            <DialogDescription>
              ユーザーIDを入力して、「{assignModalTag?.name}」タグを割り当てます。
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleAssign} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="userId" className="text-sm font-medium">
                ユーザーID <span className="text-red-500">*</span>
              </label>
              <Input
                id="userId"
                type="text"
                placeholder="例: user-uuid-1234"
                value={assignUserId}
                onChange={(e) => setAssignUserId(e.target.value)}
                disabled={isAssigning}
                required
              />
              <p className="text-xs text-gray-500">
                割り当て先のユーザーIDを入力してください
              </p>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setAssignModalTag(null);
                  setAssignUserId('');
                }}
                disabled={isAssigning}
              >
                キャンセル
              </Button>
              <Button type="submit" disabled={isAssigning}>
                {isAssigning ? '割り当て中...' : '割り当てる'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* 削除確認モーダル */}
      <Dialog open={!!deleteModalTag} onOpenChange={(open) => !open && setDeleteModalTag(null)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>タグを削除</DialogTitle>
            <DialogDescription>
              「{deleteModalTag?.name}」タグを削除してもよろしいですか？この操作は取り消せません。
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end gap-3 pt-4">
            <Button
              variant="outline"
              onClick={() => setDeleteModalTag(null)}
              disabled={isDeleting}
            >
              キャンセル
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={isDeleting}
            >
              {isDeleting ? '削除中...' : '削除する'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
