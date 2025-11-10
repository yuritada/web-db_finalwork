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

// ユーザー区分
export enum UserKategori {
  STUDENT = '学生',
  PROFESSOR = '教授',
  ASSOCIATE_PROFESSOR = '准教授',
  LECTURER = '講師',
  STAFF = '事務',
}

export interface User {
  id: string;
  username: string;
  email: string;
  kategori: UserKategori;
  gakuseki_bango?: string;
  faculty?: string;
  icon_path?: string;
}

export interface SignupRequest {
  username: string;
  email: string;
  password: string;
  kategori: UserKategori;
  gakuseki_bango?: string;
  faculty?: string;
}

// サインアップ関数 (POST /api/auth/signup)
export async function signup(data: SignupRequest): Promise<User> {
  const response = await apiClient.post<User>('/auth/signup', data);
  return response.data;
}

// ログイン関数 (POST /api/auth/login)
export async function login(username: string, password: string): Promise<LoginResponse> {
  const params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);

  const response = await apiClient.post<LoginResponse>('/auth/login', params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
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

// ====================
// Wiki関連の型定義
// ====================

export enum PermissionLevel {
  VIEW_ONLY = 'VIEW_ONLY',
  EDIT = 'EDIT',
}

export interface WikiPageBase {
  title: string;
  content: string;
}

export interface WikiPageCreate {
  title: string;
  content?: string;
}

export interface WikiPageUpdate {
  title?: string;
  content?: string;
}

export interface WikiPagePublic {
  id: number;
  title: string;
  content: string;
  creator_id: string;
  created_at: string;
  updated_at: string;
}

export interface PermissionInfo {
  user_id: string;
  permission_level: PermissionLevel;
}

export interface WikiPageDetail extends WikiPagePublic {
  permissions: PermissionInfo[];
}

export interface ShareWikiRequest {
  user_id: string;
  permission_level: PermissionLevel;
}

// ====================
// Wiki API関数
// ====================

// Wikiページ一覧取得 (GET /wiki/pages)
export async function getWikiPages(): Promise<WikiPagePublic[]> {
  const response = await apiClient.get<WikiPagePublic[]>('/wiki/pages');
  return response.data;
}

// Wikiページ詳細取得 (GET /wiki/pages/:page_id)
export async function getWikiPage(pageId: number): Promise<WikiPageDetail> {
  const response = await apiClient.get<WikiPageDetail>(`/wiki/pages/${pageId}`);
  return response.data;
}

// Wikiページ作成 (POST /wiki/pages)
export async function createWikiPage(data: WikiPageCreate): Promise<WikiPagePublic> {
  const response = await apiClient.post<WikiPagePublic>('/wiki/pages', data);
  return response.data;
}

// Wikiページ更新 (PUT /wiki/pages/:page_id)
export async function updateWikiPage(pageId: number, data: WikiPageUpdate): Promise<WikiPagePublic> {
  const response = await apiClient.put<WikiPagePublic>(`/wiki/pages/${pageId}`, data);
  return response.data;
}

// Wikiページ共有 (POST /wiki/pages/:page_id/share)
export async function shareWikiPage(pageId: number, data: ShareWikiRequest): Promise<{ success: boolean }> {
  const response = await apiClient.post<{ success: boolean }>(`/wiki/pages/${pageId}/share`, data);
  return response.data;
}

// ====================
// Tag関連の型定義
// ====================

export interface TagCreate {
  name: string;
}

export interface TagPublic {
  id: number;
  name: string;
  creator_id: string;
}

export interface UserInfo {
  id: string;
  username: string;
  email: string;
}

export interface TagDetail extends TagPublic {
  assigned_users: UserInfo[];
}

export interface TagAssignment {
  user_id: string;
}

// ====================
// Tag API関数
// ====================

// タグ一覧取得 (GET /tags)
export async function getTags(): Promise<TagPublic[]> {
  const response = await apiClient.get<TagPublic[]>('/tags');
  return response.data;
}

// タグ作成 (POST /tags)
export async function createTag(data: TagCreate): Promise<TagPublic> {
  const response = await apiClient.post<TagPublic>('/tags', data);
  return response.data;
}

// タグ詳細取得 (GET /tags/:tag_id)
export async function getTag(tagId: number): Promise<TagDetail> {
  const response = await apiClient.get<TagDetail>(`/tags/${tagId}`);
  return response.data;
}

// ユーザーにタグを割り当て (POST /tags/:tag_id/assign)
export async function assignTag(tagId: number, userId: string): Promise<{ success: boolean }> {
  const response = await apiClient.post<{ success: boolean }>(`/tags/${tagId}/assign`, {
    user_id: userId,
  });
  return response.data;
}

// タグ削除 (DELETE /tags/:tag_id)
export async function deleteTag(tagId: number): Promise<void> {
  await apiClient.delete(`/tags/${tagId}`);
}

// ====================
// Search関連の型定義
// ====================

export interface SearchResult {
  type: 'wiki' | 'tag' | 'user';
  id: number | string;
  title?: string;        // Wiki用
  snippet?: string;      // Wiki用
  name?: string;         // Tag用
  username?: string;     // User用
  email?: string;        // User用
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
}

// ====================
// Search API関数
// ====================

// 検索 (GET /search?q=keyword&type=wiki|tag|user|all)
export async function search(
  query: string,
  type: 'wiki' | 'tag' | 'user' | 'all' = 'all'
): Promise<SearchResponse> {
  const response = await apiClient.get<SearchResponse>('/search', {
    params: { q: query, type }
  });
  return response.data;
}
