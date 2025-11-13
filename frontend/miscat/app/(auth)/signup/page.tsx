'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { signup, UserKategori } from '@/lib/api';

// パスワード強度を計算
function calculatePasswordStrength(password: string): { score: number; label: string; color: string } {
  let score = 0;

  if (password.length >= 8) score += 1;
  if (password.length >= 12) score += 1;
  if (/[a-z]/.test(password)) score += 1;
  if (/[A-Z]/.test(password)) score += 1;
  if (/[0-9]/.test(password)) score += 1;
  if (/[^a-zA-Z0-9]/.test(password)) score += 1;

  if (score <= 2) return { score, label: '弱い', color: 'bg-red-500' };
  if (score <= 4) return { score, label: '普通', color: 'bg-yellow-500' };
  return { score, label: '強い', color: 'bg-green-500' };
}

export default function SignupPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [kategori, setKategori] = useState<UserKategori | ''>('');
  const [gakusekiBango, setGakusekiBango] = useState('');
  const [faculty, setFaculty] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const passwordStrength = password ? calculatePasswordStrength(password) : null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // バリデーション
      if (!username || !email || !password || !confirmPassword || !kategori) {
        setError('全ての必須項目を入力してください');
        setIsLoading(false);
        return;
      }

      // ユーザー名の長さチェック
      if (username.length < 3 || username.length > 100) {
        setError('ユーザー名は3文字以上100文字以内で入力してください');
        setIsLoading(false);
        return;
      }

      // メールアドレスの簡易バリデーション
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        setError('有効なメールアドレスを入力してください');
        setIsLoading(false);
        return;
      }

      // パスワードの長さチェック
      if (password.length < 8) {
        setError('パスワードは8文字以上で入力してください');
        setIsLoading(false);
        return;
      }

      // パスワード確認
      if (password !== confirmPassword) {
        setError('パスワードが一致しません');
        setIsLoading(false);
        return;
      }

      // サインアップ実行
      await signup({
        username,
        email,
        password,
        kategori: kategori as UserKategori,
        gakuseki_bango: gakusekiBango || undefined,
        faculty: faculty || undefined,
      });

      // サインアップ成功後、トップページへリダイレクト（認証済みなら /dashboard へ自動遷移）
      router.push('/');
    } catch (err: unknown) {
      // エラーハンドリング
      if (err instanceof Error) {
        setError(err.message || 'サインアップに失敗しました');
      } else {
        setError('サインアップに失敗しました');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-8">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">
            新規登録
          </CardTitle>
          <CardDescription className="text-center">
            アカウントを作成してください
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* ユーザー名 */}
            <div className="space-y-2">
              <label htmlFor="username" className="text-sm font-medium">
                ユーザー名 <span className="text-red-500">*</span>
              </label>
              <Input
                id="username"
                type="text"
                placeholder="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={isLoading}
                required
                autoComplete="username"
                minLength={3}
                maxLength={100}
              />
              <p className="text-xs text-gray-500">
                3-100文字
              </p>
            </div>

            {/* メールアドレス */}
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                メールアドレス <span className="text-red-500">*</span>
              </label>
              <Input
                id="email"
                type="email"
                placeholder="email@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
                required
                autoComplete="email"
              />
            </div>

            {/* パスワード */}
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium">
                パスワード <span className="text-red-500">*</span>
              </label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
                required
                autoComplete="new-password"
                minLength={8}
              />
              {/* パスワード強度インジケーター */}
              {passwordStrength && (
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all ${passwordStrength.color}`}
                        style={{ width: `${(passwordStrength.score / 6) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium">{passwordStrength.label}</span>
                  </div>
                  <p className="text-xs text-gray-500">
                    8文字以上推奨
                  </p>
                </div>
              )}
            </div>

            {/* パスワード確認 */}
            <div className="space-y-2">
              <label htmlFor="confirmPassword" className="text-sm font-medium">
                パスワード確認 <span className="text-red-500">*</span>
              </label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={isLoading}
                required
                autoComplete="new-password"
              />
              {confirmPassword && password !== confirmPassword && (
                <p className="text-xs text-red-600">
                  パスワードが一致しません
                </p>
              )}
            </div>

            {/* ユーザー区分 */}
            <div className="space-y-2">
              <label htmlFor="kategori" className="text-sm font-medium">
                ユーザー区分 <span className="text-red-500">*</span>
              </label>
              <Select
                value={kategori}
                onValueChange={(value) => setKategori(value as UserKategori)}
                disabled={isLoading}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="選択してください" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={UserKategori.STUDENT}>学生</SelectItem>
                  <SelectItem value={UserKategori.PROFESSOR}>教授</SelectItem>
                  <SelectItem value={UserKategori.ASSOCIATE_PROFESSOR}>准教授</SelectItem>
                  <SelectItem value={UserKategori.LECTURER}>講師</SelectItem>
                  <SelectItem value={UserKategori.STAFF}>事務</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* 学籍番号（学生の場合のみ表示） */}
            {kategori === UserKategori.STUDENT && (
              <div className="space-y-2">
                <label htmlFor="gakusekiBango" className="text-sm font-medium">
                  学籍番号
                </label>
                <Input
                  id="gakusekiBango"
                  type="text"
                  placeholder="例: 12345678"
                  value={gakusekiBango}
                  onChange={(e) => setGakusekiBango(e.target.value)}
                  disabled={isLoading}
                  maxLength={50}
                />
              </div>
            )}

            {/* 学部（オプション） */}
            <div className="space-y-2">
              <label htmlFor="faculty" className="text-sm font-medium">
                学部・所属（任意）
              </label>
              <Input
                id="faculty"
                type="text"
                placeholder="例: 工学部"
                value={faculty}
                onChange={(e) => setFaculty(e.target.value)}
                disabled={isLoading}
                maxLength={100}
              />
            </div>

            {/* エラーメッセージ */}
            {error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
                {error}
              </div>
            )}

            {/* サインアップボタン */}
            <Button
              type="submit"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? '登録中...' : 'アカウントを作成'}
            </Button>

            {/* ログインリンク */}
            <div className="text-center text-sm">
              <span className="text-gray-600">既にアカウントをお持ちですか？ </span>
              <Link href="/login" className="text-sky-600 hover:underline font-medium">
                ログインはこちら
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
