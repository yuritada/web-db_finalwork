import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    // HttpOnly Cookie をクリア
    const res = NextResponse.json({ message: 'Logged out successfully' });
    res.cookies.delete('access_token');

    return res;
  } catch (error) {
    console.error('Logout error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
