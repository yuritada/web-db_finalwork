'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { shareWikiPage, PermissionLevel } from '@/lib/api';

interface ShareModalProps {
  pageId: number;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function ShareModal({ pageId, isOpen, onClose, onSuccess }: ShareModalProps) {
  const [userId, setUserId] = useState('');
  const [permissionLevel, setPermissionLevel] = useState<PermissionLevel>(PermissionLevel.VIEW_ONLY);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');
    setIsLoading(true);

    try {
      // バリデーション
      if (!userId.trim()) {
        setError('ユーザーIDを入力してください');
        setIsLoading(false);
        return;
      }

      // 共有API呼び出し
      await shareWikiPage(pageId, {
        user_id: userId.trim(),
        permission_level: permissionLevel,
      });

      setSuccessMessage('共有設定が完了しました');
      setUserId('');
      setPermissionLevel(PermissionLevel.VIEW_ONLY);

      // 成功コールバック実行
      setTimeout(() => {
        onSuccess();
        handleClose();
      }, 1000);
    } catch (err: unknown) {
      // エラーハンドリング
      if (err instanceof Error) {
        setError(err.message || '共有設定に失敗しました');
      } else {
        setError('共有設定に失敗しました');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setUserId('');
    setPermissionLevel(PermissionLevel.VIEW_ONLY);
    setError('');
    setSuccessMessage('');
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Wikiページを共有</DialogTitle>
          <DialogDescription>
            ユーザーIDと権限レベルを指定して、このWikiページを共有します。
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* ユーザーID入力 */}
          <div className="space-y-2">
            <label htmlFor="userId" className="text-sm font-medium">
              ユーザーID <span className="text-red-500">*</span>
            </label>
            <Input
              id="userId"
              type="text"
              placeholder="共有するユーザーのIDを入力"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              disabled={isLoading}
              required
            />
            <p className="text-xs text-gray-500">
              例: user-uuid-1234
            </p>
          </div>

          {/* 権限レベル選択 */}
          <div className="space-y-2">
            <label htmlFor="permissionLevel" className="text-sm font-medium">
              権限レベル <span className="text-red-500">*</span>
            </label>
            <Select
              value={permissionLevel}
              onValueChange={(value) => setPermissionLevel(value as PermissionLevel)}
              disabled={isLoading}
            >
              <SelectTrigger>
                <SelectValue placeholder="権限を選択" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={PermissionLevel.VIEW_ONLY}>
                  閲覧のみ
                </SelectItem>
                <SelectItem value={PermissionLevel.EDIT}>
                  編集可能
                </SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-gray-500">
              {permissionLevel === PermissionLevel.VIEW_ONLY
                ? 'ユーザーはページを閲覧できますが、編集はできません'
                : 'ユーザーはページを閲覧・編集できます'}
            </p>
          </div>

          {/* エラーメッセージ */}
          {error && (
            <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
              {error}
            </div>
          )}

          {/* 成功メッセージ */}
          {successMessage && (
            <div className="p-3 text-sm text-green-600 bg-green-50 border border-green-200 rounded-md">
              {successMessage}
            </div>
          )}

          {/* ボタン */}
          <div className="flex justify-end gap-3 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isLoading}
            >
              キャンセル
            </Button>
            <Button
              type="submit"
              disabled={isLoading}
            >
              {isLoading ? '共有中...' : '共有する'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
