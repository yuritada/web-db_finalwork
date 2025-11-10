'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { getTag, assignTag, deleteTag, TagDetail } from '@/lib/api';
import { toast } from 'sonner';
import { useAuth } from '@/context/AuthContext';

export default function TagDetailPage() {
  const router = useRouter();
  const params = useParams();
  const { user } = useAuth();
  const tagId = Number(params.tag_id);

  const [tag, setTag] = useState<TagDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // ユーザー割り当てモーダル
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
  const [assignUserId, setAssignUserId] = useState('');
  const [isAssigning, setIsAssigning] = useState(false);

  // 削除確認モーダル
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // タグ詳細取得
  const fetchTag = async () => {
    try {
      setIsLoading(true);
      const data = await getTag(tagId);
      setTag(data);
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
    if (tagId) {
      fetchTag();
    }
  }, [tagId]);

  // ユーザー割り当て
  const handleAssign = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!assignUserId.trim()) {
      toast.error('ユーザーIDを入力してください');
      return;
    }

    setIsAssigning(true);

    try {
      await assignTag(tagId, assignUserId.trim());
      toast.success('ユーザーにタグを割り当てました');
      setIsAssignModalOpen(false);
      setAssignUserId('');
      fetchTag(); // 一覧を再取得
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
    setIsDeleting(true);

    try {
      await deleteTag(tagId);
      toast.success('タグを削除しました');
      router.push('/main/tags');
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
  const isCreator = () => {
    return tag && user && user.id === tag.creator_id;
  };

  return (
    <div className="space-y-6">
      {/* パンくず */}
      <div className="text-sm text-gray-500">
        <Link href="/main/tags" className="hover:text-gray-700 hover:underline">
          タグ管理
        </Link>
        {' / '}
        <span className="text-gray-900">
          {tag ? tag.name : 'タグ詳細'}
        </span>
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

      {/* タグ詳細 */}
      {!isLoading && tag && (
        <>
          {/* タグ情報カード */}
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-2xl">{tag.name}</CardTitle>
                  <CardDescription>
                    作成者: {tag.creator_id}
                  </CardDescription>
                </div>

                {/* アクションボタン */}
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={() => setIsAssignModalOpen(true)}
                  >
                    ユーザー割り当て
                  </Button>

                  {/* 削除ボタン（作成者のみ） */}
                  {isCreator() && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setIsDeleteModalOpen(true)}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      削除
                    </Button>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-gray-500">
                タグID: {tag.id}
              </div>
            </CardContent>
          </Card>

          {/* 割り当てられたユーザー一覧 */}
          <Card>
            <CardHeader>
              <CardTitle>割り当てられたユーザー</CardTitle>
              <CardDescription>
                このタグが割り当てられているユーザーの一覧
              </CardDescription>
            </CardHeader>
            <CardContent>
              {tag.assigned_users.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  まだユーザーが割り当てられていません
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>ユーザー名</TableHead>
                      <TableHead>メールアドレス</TableHead>
                      <TableHead>ユーザーID</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {tag.assigned_users.map((assignedUser) => (
                      <TableRow key={assignedUser.id}>
                        <TableCell className="font-medium">
                          {assignedUser.username}
                        </TableCell>
                        <TableCell>{assignedUser.email}</TableCell>
                        <TableCell className="text-gray-500 text-sm">
                          {assignedUser.id}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* ユーザー割り当てモーダル */}
      <Dialog open={isAssignModalOpen} onOpenChange={setIsAssignModalOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>ユーザーにタグを割り当て</DialogTitle>
            <DialogDescription>
              ユーザーIDを入力して、「{tag?.name}」タグを割り当てます。
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
                  setIsAssignModalOpen(false);
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
      <Dialog open={isDeleteModalOpen} onOpenChange={setIsDeleteModalOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>タグを削除</DialogTitle>
            <DialogDescription>
              「{tag?.name}」タグを削除してもよろしいですか？この操作は取り消せません。
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end gap-3 pt-4">
            <Button
              variant="outline"
              onClick={() => setIsDeleteModalOpen(false)}
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
