import axios from 'axios';

// axiosインスタンス作成 (baseURL: /api)
export const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // HttpOnly Cookieを使用するため
});

// レスポンス型定義
export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  user_id: number;
  username: string;
  display_name: string;
  bio?: string;
  created_at: string;
}

// ログイン関数 (POST /api/auth/login)
export async function login(username: string, password: string): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>('/auth/login', {
    username,
    password,
  });
  return response.data;
}

// ログアウト関数 (POST /api/auth/logout)
export async function logout(): Promise<void> {
  await apiClient.post('/auth/logout');
}

// 現在のユーザー情報取得 (GET /api/auth/me)
export async function getMe(): Promise<User> {
  const response = await apiClient.get<User>('/auth/me');
  return response.data;
}
