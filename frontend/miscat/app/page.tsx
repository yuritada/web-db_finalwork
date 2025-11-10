'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        // 認証済み → /main へリダイレクト
        router.push('/main');
      } else {
        // 未認証 → /login へリダイレクト
        router.push('/login');
      }
    }
  }, [isAuthenticated, isLoading, router]);

  // リダイレクト中はローディング表示
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-sky-500 border-r-transparent"></div>
        <p className="mt-2 text-sm text-gray-600">読み込み中...</p>
      </div>
    </div>
  );
}
