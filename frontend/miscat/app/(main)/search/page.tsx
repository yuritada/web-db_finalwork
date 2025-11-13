'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { search, SearchResult } from '@/lib/api';
import { toast } from 'sonner';

export default function SearchPage() {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState<'wiki' | 'tag' | 'user' | 'all'>('all');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  // 検索実行
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!query.trim()) {
      toast.error('検索キーワードを入力してください');
      return;
    }

    setIsSearching(true);
    setHasSearched(true);

    try {
      const response = await search(query.trim(), searchType);
      setResults(response.results);
      setTotal(response.total);

      if (response.total === 0) {
        toast.info('検索結果が見つかりませんでした');
      } else {
        toast.success(`${response.total}件の結果が見つかりました`);
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error('検索に失敗しました: ' + err.message);
      } else {
        toast.error('検索に失敗しました');
      }
      setResults([]);
      setTotal(0);
    } finally {
      setIsSearching(false);
    }
  };

  // 結果タイプに応じたアイコン
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'wiki':
        return '📄';
      case 'tag':
        return '🏷️';
      case 'user':
        return '👤';
      default:
        return '🔍';
    }
  };

  // 結果タイプに応じたラベル
  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'wiki':
        return 'Wiki';
      case 'tag':
        return 'タグ';
      case 'user':
        return 'ユーザー';
      default:
        return '';
    }
  };

  // 検索タイプのラベル
  const getSearchTypeLabel = (type: string) => {
    switch (type) {
      case 'all':
        return 'すべて';
      case 'wiki':
        return 'Wiki';
      case 'tag':
        return 'タグ';
      case 'user':
        return 'ユーザー';
      default:
        return '';
    }
  };

  // 結果クリック時の処理
  const handleResultClick = (result: SearchResult) => {
    if (result.type === 'wiki') {
      router.push(`/wiki/${result.id}`);
    } else if (result.type === 'tag') {
      router.push(`/tags/${result.id}`);
    }
    // userの場合は詳細ページがないため何もしない
  };

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">検索</h1>
        <p className="mt-2 text-gray-600">
          Wiki、タグ、ユーザーを検索できます。
        </p>
      </div>

      {/* 検索フォーム */}
      <Card>
        <CardHeader>
          <CardTitle>検索条件</CardTitle>
          <CardDescription>
            キーワードと検索対象を指定してください
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="space-y-4">
            {/* 検索キーワード */}
            <div className="space-y-2">
              <label htmlFor="query" className="text-sm font-medium">
                キーワード <span className="text-red-500">*</span>
              </label>
              <Input
                id="query"
                type="text"
                placeholder="検索キーワードを入力"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={isSearching}
                required
              />
            </div>

            {/* 検索タイプ */}
            <div className="space-y-2">
              <label htmlFor="searchType" className="text-sm font-medium">
                検索対象
              </label>
              <Select
                value={searchType}
                onValueChange={(value) => setSearchType(value as 'wiki' | 'tag' | 'user' | 'all')}
                disabled={isSearching}
              >
                <SelectTrigger>
                  <SelectValue placeholder="検索対象を選択" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">すべて</SelectItem>
                  <SelectItem value="wiki">Wiki</SelectItem>
                  <SelectItem value="tag">タグ</SelectItem>
                  <SelectItem value="user">ユーザー</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* 検索ボタン */}
            <Button type="submit" disabled={isSearching} className="w-full">
              {isSearching ? '検索中...' : '検索'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* 検索結果 */}
      {hasSearched && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-900">
              検索結果
              {total > 0 && (
                <span className="ml-2 text-sm font-normal text-gray-500">
                  ({total}件)
                </span>
              )}
            </h2>
            {query && (
              <div className="text-sm text-gray-500">
                「{query}」を「{getSearchTypeLabel(searchType)}」から検索
              </div>
            )}
          </div>

          {/* ローディング */}
          {isSearching && (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-sky-500 border-r-transparent"></div>
                <p className="mt-2 text-sm text-gray-600">検索中...</p>
              </div>
            </div>
          )}

          {/* 結果一覧 */}
          {!isSearching && (
            <>
              {results.length === 0 ? (
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center py-12">
                      <p className="text-gray-500">検索結果が見つかりませんでした</p>
                      <p className="text-sm text-gray-400 mt-2">
                        キーワードを変更して再度検索してみてください
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid grid-cols-1 gap-4">
                  {results.map((result, index) => (
                    <Card
                      key={`${result.type}-${result.id}-${index}`}
                      className={
                        result.type !== 'user'
                          ? 'hover:shadow-md transition-shadow cursor-pointer'
                          : ''
                      }
                      onClick={() => result.type !== 'user' && handleResultClick(result)}
                    >
                      <CardHeader>
                        <div className="flex items-start gap-3">
                          <div className="text-2xl">{getTypeIcon(result.type)}</div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <CardTitle className="text-lg">
                                {result.type === 'wiki' && result.title}
                                {result.type === 'tag' && result.name}
                                {result.type === 'user' && result.username}
                              </CardTitle>
                              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                                {getTypeLabel(result.type)}
                              </span>
                            </div>
                            {result.type === 'wiki' && result.snippet && (
                              <CardDescription className="mt-2">
                                {result.snippet}
                              </CardDescription>
                            )}
                            {result.type === 'user' && result.email && (
                              <CardDescription className="mt-1">
                                {result.email}
                              </CardDescription>
                            )}
                          </div>
                        </div>
                      </CardHeader>
                    </Card>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
