import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://backend:8000';

export async function POST(request: NextRequest) {
  try {
    // リクエストボディから username, password を取得 (form-urlencoded形式)
    const body = await request.text();
    const params = new URLSearchParams(body);
    const username = params.get('username');
    const password = params.get('password');

    if (!username || !password) {
      return NextResponse.json(
        { error: 'Username and password are required' },
        { status: 400 }
      );
    }

    // FastAPI の /auth/token に application/x-www-form-urlencoded で送信
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${BACKEND_URL}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.detail || 'Authentication failed' },
        { status: response.status }
      );
    }

    const data = await response.json();
    const { access_token, token_type } = data;

    // HttpOnly Cookie に access_token を設定
    const res = NextResponse.json({ access_token, token_type });
    res.cookies.set('access_token', access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7, // 7日間
      path: '/',
    });

    return res;
  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
