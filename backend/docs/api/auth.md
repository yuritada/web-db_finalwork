# 認証API (`/auth`)

## 概要

認証APIは、ユーザー登録とログイン機能を提供します。OAuth2準拠のJWT（JSON Web Token）認証を使用しています。

## エンドポイント一覧

| メソッド | パス | 説明 | 認証 |
|---------|------|------|------|
| POST | `/auth/signup` | ユーザー登録 | 不要 |
| POST | `/auth/token` | ログイン（JWT発行） | 不要 |

---

## POST /auth/signup

ユーザー登録エンドポイント。v3仕様に従い、学生以外の場合は`gakuseki_bango`を自動生成します。

### エンドポイント情報

- **URL**: `/auth/signup`
- **メソッド**: `POST`
- **認証**: 不要
- **Content-Type**: `application/json`

### リクエストボディ

**スキーマ**: `UserCreate`

```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string",
  "kategori": "学生" | "教授" | "准教授" | "講師" | "事務",
  "gakuseki_bango": "string (optional)",
  "faculty": "string (optional)"
}
```

**フィールド詳細**:

| フィールド | 型 | 必須 | 説明 | 制約 |
|-----------|-----|------|------|------|
| username | string | ✅ | ユーザー名 | 3-100文字、一意 |
| email | string | ✅ | メールアドレス | Email形式、一意 |
| password | string | ✅ | パスワード | 8文字以上 |
| kategori | enum | ✅ | ユーザーカテゴリー | 5種類から選択 |
| gakuseki_bango | string | ❌ | 学籍番号 | 学生の場合は必須、教員/事務は自動生成 |
| faculty | string | ❌ | 学部・所属 | 最大100文字 |

### レスポンス

**成功 (201 Created)**:

**スキーマ**: `UserPublic`

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "username": "johndoe",
  "email": "johndoe@example.com",
  "kategori": "学生",
  "gakuseki_bango": "S12345678",
  "faculty": "情報学部",
  "icon_path": null
}
```

### リクエスト例

#### curl

```bash
# 学生の場合（gakuseki_bango指定）
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student01",
    "email": "student01@example.com",
    "password": "securepass123",
    "kategori": "学生",
    "gakuseki_bango": "S12345678",
    "faculty": "情報学部"
  }'

# 教員の場合（gakuseki_bango自動生成）
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "prof_tanaka",
    "email": "tanaka@example.com",
    "password": "profpass456",
    "kategori": "教授",
    "faculty": "情報学部"
  }'
```

#### Python (requests)

```python
import requests

url = "http://localhost:8000/auth/signup"
data = {
    "username": "student01",
    "email": "student01@example.com",
    "password": "securepass123",
    "kategori": "学生",
    "gakuseki_bango": "S12345678",
    "faculty": "情報学部"
}

response = requests.post(url, json=data)
if response.status_code == 201:
    user = response.json()
    print(f"User created: {user['username']} (ID: {user['id']})")
else:
    print(f"Error: {response.json()}")
```

#### JavaScript (fetch)

```javascript
const signup = async (userData) => {
  const response = await fetch('http://localhost:8000/auth/signup', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: 'student01',
      email: 'student01@example.com',
      password: 'securepass123',
      kategori: '学生',
      gakuseki_bango: 'S12345678',
      faculty: '情報学部'
    })
  });

  if (response.status === 201) {
    const user = await response.json();
    console.log('User created:', user);
  } else {
    const error = await response.json();
    console.error('Error:', error);
  }
};
```

#### TypeScript (axios)

```typescript
import axios from 'axios';

interface UserCreateRequest {
  username: string;
  email: string;
  password: string;
  kategori: '学生' | '教授' | '准教授' | '講師' | '事務';
  gakuseki_bango?: string;
  faculty?: string;
}

const signup = async (userData: UserCreateRequest) => {
  try {
    const response = await axios.post(
      'http://localhost:8000/auth/signup',
      userData
    );
    console.log('User created:', response.data);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('Signup failed:', error.response?.data);
      throw error;
    }
  }
};
```

### エラーレスポンス

#### 400 Bad Request - ユーザー名重複

```json
{
  "detail": "Username already registered"
}
```

#### 400 Bad Request - メールアドレス重複

```json
{
  "detail": "Email already registered"
}
```

#### 422 Unprocessable Entity - バリデーションエラー

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### ビジネスロジック（v3仕様）

**gakuseki_bango自動生成ロジック**:

```python
# app/db/create.py より抜粋
if user_data.kategori != UserKategori.STUDENT:
    gakuseki_bango = f"staff_{uuid.uuid4().hex[:8]}"
```

- **学生**: リクエストの`gakuseki_bango`をそのまま使用
- **教員・事務**: `staff_` + 8文字のランダムな16進数文字列を自動生成
  - 例: `staff_a1b2c3d4`

---

## POST /auth/token

ログインエンドポイント。ユーザー名とパスワードを検証し、JWTアクセストークンを発行します。

### エンドポイント情報

- **URL**: `/auth/token`
- **メソッド**: `POST`
- **認証**: 不要
- **Content-Type**: `application/x-www-form-urlencoded`（OAuth2準拠）

### リクエストボディ

**フォーマット**: `application/x-www-form-urlencoded`

```
username=student01&password=securepass123
```

**フィールド**:

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| username | string | ✅ | ユーザー名 |
| password | string | ✅ | パスワード |
| grant_type | string | ❌ | OAuth2 grant type（デフォルト: "password"） |
| scope | string | ❌ | OAuth2 scope（デフォルト: ""） |

### レスポンス

**成功 (200 OK)**:

**スキーマ**: `Token`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHVkZW50MDEiLCJleHAiOjE3MzY0MjUyMDB9.signature",
  "token_type": "bearer"
}
```

**フィールド詳細**:

| フィールド | 型 | 説明 |
|-----------|-----|------|
| access_token | string | JWTアクセストークン（有効期限: 60分） |
| token_type | string | 常に "bearer" |

### リクエスト例

#### curl

```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student01&password=securepass123"
```

#### Python (requests)

```python
import requests

url = "http://localhost:8000/auth/token"
data = {
    "username": "student01",
    "password": "securepass123"
}

response = requests.post(url, data=data)
if response.status_code == 200:
    token_data = response.json()
    access_token = token_data["access_token"]
    print(f"Access token: {access_token}")
else:
    print(f"Login failed: {response.json()}")
```

#### JavaScript (fetch)

```javascript
const login = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  const response = await fetch('http://localhost:8000/auth/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData
  });

  if (response.ok) {
    const data = await response.json();
    // トークンをlocalStorageに保存（本番環境ではHttpOnly Cookieを推奨）
    localStorage.setItem('access_token', data.access_token);
    return data;
  } else {
    const error = await response.json();
    throw new Error(error.detail);
  }
};
```

#### TypeScript (axios)

```typescript
import axios from 'axios';

interface TokenResponse {
  access_token: string;
  token_type: string;
}

const login = async (username: string, password: string): Promise<TokenResponse> => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  try {
    const response = await axios.post<TokenResponse>(
      'http://localhost:8000/auth/token',
      formData,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('Login failed:', error.response?.data);
      throw error;
    }
    throw error;
  }
};
```

### エラーレスポンス

#### 401 Unauthorized - 認証失敗

```json
{
  "detail": "Incorrect username or password"
}
```

**HTTPヘッダー**:
```
WWW-Authenticate: Bearer
```

### JWTトークンの構造

**デコードされたペイロード例**:

```json
{
  "sub": "student01",
  "exp": 1736425200
}
```

**フィールド説明**:

| フィールド | 説明 |
|-----------|------|
| sub | Subject: ユーザー名 |
| exp | Expiration: 有効期限（UNIXタイムスタンプ） |

### セキュリティ要件

1. **パスワードハッシュ化**: bcryptを使用
2. **JWT署名**: HMAC SHA-256アルゴリズム
3. **トークン有効期限**: 60分（環境変数で設定可能）
4. **HTTPS必須**: 本番環境ではHTTPSを使用してトークンを保護

### 使用例: 認証付きリクエスト

トークン取得後、他のAPIエンドポイントにアクセスする際は`Authorization`ヘッダーにトークンを含めます。

```bash
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

```python
headers = {
    "Authorization": f"Bearer {access_token}"
}
response = requests.get("http://localhost:8000/users/me", headers=headers)
```

```typescript
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const user = await api.get('/users/me');
```
