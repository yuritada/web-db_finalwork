'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { search, SearchResult, addChannelMember } from '@/lib/api';
import { toast } from 'sonner';

interface AddMemberDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  channelId: number;
  onMemberAdded: () => void;
}

export function AddMemberDialog({ open, onOpenChange, channelId, onMemberAdded }: AddMemberDialogProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isAdding, setIsAdding] = useState(false);

  // ユーザー検索
  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast.error('検索キーワードを入力してください');
      return;
    }

    try {
      setIsSearching(true);
      const result = await search(searchQuery, 'user');
      setSearchResults(result.results.filter(r => r.type === 'user'));

      if (result.results.length === 0) {
        toast.info('ユーザーが見つかりませんでした');
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error('検索に失敗しました: ' + err.message);
      } else {
        toast.error('検索に失敗しました');
      }
    } finally {
      setIsSearching(false);
    }
  };

  // ユーザー選択してメンバー追加
  const handleAddMember = async (userId: string, username: string) => {
    try {
      setIsAdding(true);
      await addChannelMember(channelId, userId);
      toast.success(`${username} をチャンネルに追加しました`);
      onOpenChange(false);
      onMemberAdded(); // メンバーリストを再取得
      // ダイアログを閉じた後にリセット
      setTimeout(() => {
        setSearchQuery('');
        setSearchResults([]);
      }, 300);
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error('メンバー追加に失敗しました: ' + err.message);
      } else {
        toast.error('メンバー追加に失敗しました');
      }
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>チャンネルにメンバーを追加</DialogTitle>
          <DialogDescription>
            追加したいユーザーを検索してください
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* 検索フォーム */}
          <div className="flex gap-2">
            <Input
              placeholder="ユーザー名で検索..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleSearch();
                }
              }}
              disabled={isAdding}
            />
            <Button
              onClick={handleSearch}
              disabled={isSearching || isAdding}
            >
              {isSearching ? '検索中...' : '検索'}
            </Button>
          </div>

          {/* 検索結果 */}
          <div className="space-y-2 max-h-[400px] overflow-y-auto">
            {searchResults.length > 0 ? (
              searchResults.map((result) => (
                <div
                  key={result.id}
                  className="flex items-center justify-between p-3 rounded-lg border hover:bg-gray-50 transition-colors"
                >
                  <div className="flex-1">
                    <div className="font-medium">{result.username}</div>
                    {result.email && (
                      <div className="text-sm text-gray-500">{result.email}</div>
                    )}
                  </div>
                  <Button
                    size="sm"
                    onClick={() => handleAddMember(result.id as string, result.username || '')}
                    disabled={isAdding}
                  >
                    {isAdding ? '追加中...' : '追加'}
                  </Button>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500 text-sm">
                {searchQuery ? '検索結果がありません' : 'ユーザー名を入力して検索してください'}
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
