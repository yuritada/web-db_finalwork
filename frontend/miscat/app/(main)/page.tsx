'use client';

import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function MainPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      {/* ウェルカムメッセージ */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          ようこそ、{user?.username}さん
        </h1>
        <p className="mt-2 text-gray-600">
          Miscatダッシュボードへようこそ。以下の機能が利用可能になる予定です。
        </p>
      </div>

      {/* ユーザー情報カード */}
      <Card>
        <CardHeader>
          <CardTitle>アカウント情報</CardTitle>
          <CardDescription>現在のユーザー情報</CardDescription>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">ユーザー名</dt>
              <dd className="mt-1 text-sm text-gray-900">{user?.username}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">メールアドレス</dt>
              <dd className="mt-1 text-sm text-gray-900">{user?.email}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">区分</dt>
              <dd className="mt-1 text-sm text-gray-900">{user?.kategori}</dd>
            </div>
            {user?.gakuseki_bango && (
              <div>
                <dt className="text-sm font-medium text-gray-500">学籍番号</dt>
                <dd className="mt-1 text-sm text-gray-900">{user.gakuseki_bango}</dd>
              </div>
            )}
            {user?.faculty && (
              <div>
                <dt className="text-sm font-medium text-gray-500">学部・所属</dt>
                <dd className="mt-1 text-sm text-gray-900">{user.faculty}</dd>
              </div>
            )}
          </dl>
        </CardContent>
      </Card>

      {/* 機能紹介カード */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {/* Wiki */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Wiki</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">
              知識を共有するための Wiki ページを作成・編集できます。
            </p>
            <div className="mt-4">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                準備中
              </span>
            </div>
          </CardContent>
        </Card>

        {/* チャンネル */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">チャンネル</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">
              テーマ別のチャンネルでメッセージを共有できます。
            </p>
            <div className="mt-4">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                準備中
              </span>
            </div>
          </CardContent>
        </Card>

        {/* タグ */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">タグ</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">
              興味のあるタグをフォローして情報を整理できます。
            </p>
            <div className="mt-4">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                準備中
              </span>
            </div>
          </CardContent>
        </Card>

        {/* DM */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">DM</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">
              他のユーザーと1対1でメッセージを送受信できます。
            </p>
            <div className="mt-4">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                準備中
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* お知らせ */}
      <Card>
        <CardHeader>
          <CardTitle>お知らせ</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex gap-3">
              <div className="flex-shrink-0">
                <div className="h-2 w-2 mt-2 rounded-full bg-sky-500"></div>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">
                  Phase 1 が完了しました
                </p>
                <p className="text-sm text-gray-600">
                  ユーザー認証機能が利用可能になりました。
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <div className="flex-shrink-0">
                <div className="h-2 w-2 mt-2 rounded-full bg-gray-300"></div>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">
                  Phase 2 準備中
                </p>
                <p className="text-sm text-gray-600">
                  Wiki、チャンネル、タグ、DMの各機能を順次実装予定です。
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
