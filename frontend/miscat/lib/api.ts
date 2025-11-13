import axios from 'axios';

// バックエンドURL（環境変数から取得、デフォルトはlocalhost:8000）
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// トークン管理関数
const TOKEN_KEY = 'access_token';

export function setAuthToken(token: string) {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

export function getAuthToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(TOKEN_KEY);
  }
  return null;
}

export function removeAuthToken() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY);
  }
}

// axiosインスタンス作成（バックエンド直接接続用）
export const apiClient = axios.create({
  baseURL: BACKEND_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // CORS対応
});

// リクエストインターセプター: 認証トークンをヘッダーに追加
apiClient.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

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
// Next.js API Routeを経由（Cookie管理のため）
export async function signup(data: SignupRequest): Promise<User> {
  const response = await axios.post<User>('/api/auth/signup', data);
  return response.data;
}

// ログイン関数 (POST /api/auth/login)
// Next.js API Routeを経由（Cookie管理のため）
export async function login(username: string, password: string): Promise<LoginResponse> {
  const params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);

  const response = await axios.post<LoginResponse>('/api/auth/login', params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  // トークンをlocalStorageに保存
  if (response.data.access_token) {
    setAuthToken(response.data.access_token);
  }

  return response.data;
}

// ログアウト関数 (POST /api/auth/logout)
// Next.js API Routeを経由（Cookie管理のため）
export async function logout(): Promise<void> {
  await axios.post('/api/auth/logout');
  // トークンをlocalStorageから削除
  removeAuthToken();
}

// 現在のユーザー情報取得 (GET /api/auth/me)
// Next.js API Routeを経由（Cookie管理のため）
export async function getMe(): Promise<User> {
  const response = await axios.get<User>('/api/auth/me');
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

// Wikiページ共有解除 (DELETE /wiki/pages/:page_id/share/:user_id)
export async function unshareWikiPage(pageId: number, userId: string): Promise<{ success: boolean }> {
  const response = await apiClient.delete<{ success: boolean }>(`/wiki/pages/${pageId}/share/${userId}`);
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

// ユーザーのタグ割り当て解除 (DELETE /tags/:tag_id/assign/:user_id)
export async function unassignTag(tagId: number, userId: string): Promise<{ success: boolean }> {
  const response = await apiClient.delete<{ success: boolean }>(`/tags/${tagId}/assign/${userId}`);
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

// ====================
// Channel関連の型定義
// ====================

export interface ChannelCreate {
  name: string;
  description?: string;
  is_private?: boolean;
}

export interface ChannelPublic {
  id: number;
  name: string;
  description?: string;
  is_private: boolean;
}

export interface ChannelDetail extends ChannelPublic {
  created_at: string;
  member_count: number;
  members: UserInfo[];
}

export interface Message {
  id: number;
  sender_id: string;
  sender_username: string;
  content: string;
  channel_id?: number;
  receiver_id?: string;
  created_at: string;
}

export interface MessageCreate {
  content: string;
}

export interface MemberAdd {
  user_id: string;
}

// ====================
// Channel API関数
// ====================

// チャンネル一覧取得 (GET /channels)
export async function getChannels(): Promise<ChannelPublic[]> {
  const response = await apiClient.get<ChannelPublic[]>('/channels');
  return response.data;
}

// チャンネル作成 (POST /channels)
export async function createChannel(data: ChannelCreate): Promise<ChannelPublic> {
  const response = await apiClient.post<ChannelPublic>('/channels', data);
  return response.data;
}

// チャンネル詳細取得 (GET /channels/:channel_id)
export async function getChannel(channelId: number): Promise<ChannelDetail> {
  const response = await apiClient.get<ChannelDetail>(`/channels/${channelId}`);
  return response.data;
}

// チャンネルメッセージ一覧取得 (GET /channels/:channel_id/messages)
export async function getChannelMessages(
  channelId: number,
  limit: number = 100,
  offset: number = 0
): Promise<Message[]> {
  const response = await apiClient.get<Message[]>(`/channels/${channelId}/messages`, {
    params: { limit, offset }
  });
  return response.data;
}

// チャンネルメッセージ送信 (POST /channels/:channel_id/messages)
export async function sendChannelMessage(
  channelId: number,
  data: MessageCreate
): Promise<Message> {
  const response = await apiClient.post<Message>(`/channels/${channelId}/messages`, data);
  return response.data;
}

// チャンネルメンバー追加 (POST /channels/:channel_id/members)
// Note: Worker2実装にはmembers APIがないため、Phase 5実装予定
export async function addChannelMember(
  channelId: number,
  userId: string
): Promise<{ success: boolean }> {
  const response = await apiClient.post<{ success: boolean }>(
    `/channels/${channelId}/members`,
    { user_id: userId }
  );
  return response.data;
}

// ====================
// DM関連の型定義
// ====================

export interface DMConversation {
  user_id: string;
  username: string;
  last_message?: string;
  last_message_at?: string;
  unread_count?: number;
}

export interface DMMessageCreate {
  receiver_id: string;
  content: string;
}

// ====================
// DM API関数
// ====================

// DM会話一覧取得 (GET /messages/dm)
export async function getDMConversations(): Promise<DMConversation[]> {
  const response = await apiClient.get<DMConversation[]>('/messages/dm');
  return response.data;
}

// 特定ユーザーとのDM履歴取得 (GET /messages/dm/{user_id})
export async function getDMMessages(
  userId: string,
  limit: number = 50,
  offset: number = 0
): Promise<Message[]> {
  const response = await apiClient.get<Message[]>(`/messages/dm/${userId}`, {
    params: { limit, offset }
  });
  return response.data;
}

// DMメッセージ送信 (POST /messages/dm)
export async function sendDMMessage(data: DMMessageCreate): Promise<Message> {
  const response = await apiClient.post<Message>('/messages/dm', data);
  return response.data;
}
