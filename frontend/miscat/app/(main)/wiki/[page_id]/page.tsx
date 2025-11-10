'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { getWikiPage, updateWikiPage, WikiPageDetail, PermissionLevel } from '@/lib/api';
import { ShareModal } from '@/components/wiki/ShareModal';
import { useAuth } from '@/context/AuthContext';

export default function WikiDetailPage() {
  const router = useRouter();
  const params = useParams();
  const { user } = useAuth();
  const pageId = Number(params.page_id);

  const [page, setPage] = useState<WikiPageDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // 編集モード
  const [isEditMode, setIsEditMode] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState('');

  // 共有モーダル
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);

  // ページ詳細取得
  const fetchPage = async () => {
    try {
      setIsLoading(true);
      setError('');
      const data = await getWikiPage(pageId);
      setPage(data);
      setEditTitle(data.title);
      setEditContent(data.content);
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
    if (pageId) {
      fetchPage();
    }
  }, [pageId]);

  // 編集権限チェック
  const canEdit = () => {
    if (!page || !user) return false;

    // 作成者は常に編集可能
    if (page.creator_id === user.id) return true;

    // 権限リストをチェック
    const userPermission = page.permissions.find(p => p.user_id === user.id);
    return userPermission?.permission_level === PermissionLevel.EDIT;
  };

  // 編集モード開始
  const handleStartEdit = () => {
    setIsEditMode(true);
    setSaveError('');
  };

  // 編集キャンセル
  const handleCancelEdit = () => {
    setIsEditMode(false);
    setSaveError('');
    // 元の値に戻す
    if (page) {
      setEditTitle(page.title);
      setEditContent(page.content);
    }
  };

  // 保存
  const handleSave = async () => {
    setSaveError('');
    setIsSaving(true);

    try {
      if (!editTitle.trim()) {
        setSaveError('タイトルを入力してください');
        setIsSaving(false);
        return;
      }

      await updateWikiPage(pageId, {
        title: editTitle.trim(),
        content: editContent.trim(),
      });

      // 再取得
      await fetchPage();
      setIsEditMode(false);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setSaveError(err.message || '保存に失敗しました');
      } else {
        setSaveError('保存に失敗しました');
      }
    } finally {
      setIsSaving(false);
    }
  };

  // 共有成功時
  const handleShareSuccess = () => {
    fetchPage(); // 権限リストを更新
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

  // 権限レベル表示用
  const getPermissionLabel = (level: PermissionLevel) => {
    return level === PermissionLevel.VIEW_ONLY ? '閲覧のみ' : '編集可能';
  };

  return (
    <div className="space-y-6">
      {/* パンくず */}
      <div className="text-sm text-gray-500">
        <Link href="/main/wiki" className="hover:text-gray-700 hover:underline">
          Wiki
        </Link>
        {' / '}
        <span className="text-gray-900">
          {page ? page.title : 'ページ詳細'}
        </span>
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

      {/* ページコンテンツ */}
      {!isLoading && page && (
        <>
          {/* ページカード */}
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {isEditMode ? (
                    <Input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      disabled={isSaving}
                      className="text-2xl font-bold mb-2"
                      placeholder="タイトル"
                    />
                  ) : (
                    <CardTitle className="text-2xl">{page.title}</CardTitle>
                  )}
                  <CardDescription>
                    作成者: {page.creator_id}
                  </CardDescription>
                </div>

                {/* アクションボタン */}
                <div className="flex gap-2">
                  {canEdit() && (
                    <>
                      {isEditMode ? (
                        <>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={handleCancelEdit}
                            disabled={isSaving}
                          >
                            キャンセル
                          </Button>
                          <Button
                            size="sm"
                            onClick={handleSave}
                            disabled={isSaving}
                          >
                            {isSaving ? '保存中...' : '保存'}
                          </Button>
                        </>
                      ) : (
                        <Button
                          size="sm"
                          onClick={handleStartEdit}
                        >
                          編集
                        </Button>
                      )}
                    </>
                  )}

                  {/* 共有ボタン（作成者のみ） */}
                  {page.creator_id === user?.id && !isEditMode && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setIsShareModalOpen(true)}
                    >
                      共有
                    </Button>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* 保存エラー */}
              {saveError && (
                <div className="mb-4 p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
                  {saveError}
                </div>
              )}

              {/* コンテンツ */}
              <div className="space-y-4">
                {isEditMode ? (
                  <Textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    disabled={isSaving}
                    rows={12}
                    placeholder="ここに内容を入力..."
                    className="font-mono"
                  />
                ) : (
                  <div className="prose max-w-none">
                    <pre className="whitespace-pre-wrap text-sm text-gray-700 bg-gray-50 p-4 rounded-md">
                      {page.content || '（内容なし）'}
                    </pre>
                  </div>
                )}
              </div>

              {/* メタ情報 */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="flex gap-6 text-sm text-gray-500">
                  <div>
                    作成日時: {formatDate(page.created_at)}
                  </div>
                  <div>
                    最終更新: {formatDate(page.updated_at)}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 権限リスト（作成者のみ表示） */}
          {page.creator_id === user?.id && page.permissions.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">共有設定</CardTitle>
                <CardDescription>
                  このページを共有しているユーザーの一覧
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {page.permissions.map((permission) => (
                    <div
                      key={permission.user_id}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-md"
                    >
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {permission.user_id}
                        </p>
                      </div>
                      <div>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          permission.permission_level === PermissionLevel.EDIT
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {getPermissionLabel(permission.permission_level)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}

      {/* 共有モーダル */}
      <ShareModal
        pageId={pageId}
        isOpen={isShareModalOpen}
        onClose={() => setIsShareModalOpen(false)}
        onSuccess={handleShareSuccess}
      />
    </div>
  );
}
