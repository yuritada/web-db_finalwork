'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function Home() {
  const router = useRouter();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-sky-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="text-center space-y-2">
          <CardTitle className="text-3xl font-bold text-sky-600">Miscat</CardTitle>
          <CardDescription className="text-base">
            情報共有プラットフォーム
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center text-sm text-gray-600 mb-6">
            <p>学生、教員、事務スタッフのための</p>
            <p>統合コミュニケーションプラットフォーム</p>
          </div>

          <div className="space-y-3">
            <Button
              onClick={() => router.push('/login')}
              className="w-full h-12 text-lg font-medium bg-sky-600 hover:bg-sky-700"
              size="lg"
            >
              ログイン
            </Button>

            <Button
              onClick={() => router.push('/signup')}
              variant="outline"
              className="w-full h-12 text-lg font-medium border-sky-600 text-sky-600 hover:bg-sky-50"
              size="lg"
            >
              新規登録（サインアップ）
            </Button>
          </div>

          <div className="pt-4 text-center text-xs text-gray-500">
            <p>初めての方は「新規登録」から</p>
            <p>アカウントを作成してください</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
