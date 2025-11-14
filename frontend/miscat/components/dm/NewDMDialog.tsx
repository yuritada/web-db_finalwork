'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { search, SearchResult } from '@/lib/api';
import { toast } from 'sonner';

interface NewDMDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function NewDMDialog({ open, onOpenChange }: NewDMDialogProps) {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);

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

  // ユーザー選択してDM開始
  const handleSelectUser = (userId: string, username: string) => {
    onOpenChange(false);
    router.push(`/dm/${userId}?username=${encodeURIComponent(username)}`);
    // ダイアログを閉じた後にリセット
    setTimeout(() => {
      setSearchQuery('');
      setSearchResults([]);
    }, 300);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>新しいDMを開始</DialogTitle>
          <DialogDescription>
            メッセージを送りたいユーザーを検索してください
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
            />
            <Button
              onClick={handleSearch}
              disabled={isSearching}
            >
              {isSearching ? '検索中...' : '検索'}
            </Button>
          </div>

          {/* 検索結果 */}
          <div className="space-y-2 max-h-[400px] overflow-y-auto">
            {searchResults.length > 0 ? (
              searchResults.map((result) => (
                <button
                  key={result.id}
                  onClick={() => handleSelectUser(result.id as string, result.username || '')}
                  className="w-full text-left p-3 rounded-lg border hover:bg-gray-50 transition-colors"
                >
                  <div className="font-medium">{result.username}</div>
                  {result.email && (
                    <div className="text-sm text-gray-500">{result.email}</div>
                  )}
                </button>
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
