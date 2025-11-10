import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://backend:8000';

export async function POST(request: NextRequest) {
  try {
    // リクエストボディを取得
    const body = await request.json();
    const { username, email, password, kategori, gakuseki_bango, faculty } = body;

    // バリデーション
    if (!username || !email || !password || !kategori) {
      return NextResponse.json(
        { error: 'Username, email, password, and kategori are required' },
        { status: 400 }
      );
    }

    // FastAPI の /auth/signup に送信
    const signupResponse = await fetch(`${BACKEND_URL}/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username,
        email,
        password,
        kategori,
        gakuseki_bango: gakuseki_bango || null,
        faculty: faculty || null,
      }),
    });

    if (!signupResponse.ok) {
      const error = await signupResponse.json();
      return NextResponse.json(
        { error: error.detail || 'Signup failed' },
        { status: signupResponse.status }
      );
    }

    const userData = await signupResponse.json();

    // サインアップ成功後、自動ログイン処理
    // FastAPI の /auth/token に application/x-www-form-urlencoded で送信
    const loginFormData = new URLSearchParams();
    loginFormData.append('username', username);
    loginFormData.append('password', password);

    const loginResponse = await fetch(`${BACKEND_URL}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: loginFormData.toString(),
    });

    if (!loginResponse.ok) {
      // ログインに失敗した場合でも、サインアップは成功しているのでユーザーデータを返す
      console.error('Auto-login failed after signup');
      return NextResponse.json(userData, { status: 201 });
    }

    const loginData = await loginResponse.json();
    const { access_token } = loginData;

    // HttpOnly Cookie に access_token を設定
    const res = NextResponse.json(userData, { status: 201 });
    res.cookies.set('access_token', access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7, // 7日間
      path: '/',
    });

    return res;
  } catch (error) {
    console.error('Signup error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
