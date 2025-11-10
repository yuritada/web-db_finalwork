"""
Search schemas (v3)
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import uuid


class SearchRequest(BaseModel):
    """検索リクエストスキーマ"""
    query: str = Field(..., min_length=1, description="検索キーワード")
    search_type: Literal["wiki", "tag", "user", "all"] = Field(
        default="all",
        description="検索対象タイプ"
    )


class SearchResult(BaseModel):
    """検索結果スキーマ（柔軟な構造）"""
    type: Literal["wiki", "tag", "user"] = Field(..., description="結果タイプ")
    id: int | str = Field(..., description="結果ID（WikiとTagはint、UserはUUID）")

    # Wiki用フィールド
    title: Optional[str] = Field(None, description="Wikiページタイトル")
    snippet: Optional[str] = Field(None, description="Wikiページ抜粋")

    # Tag用フィールド
    name: Optional[str] = Field(None, description="タグ名")

    # User用フィールド
    username: Optional[str] = Field(None, description="ユーザー名")
    email: Optional[str] = Field(None, description="メールアドレス")


class SearchResponse(BaseModel):
    """検索レスポンススキーマ"""
    results: List[SearchResult] = Field(default=[], description="検索結果リスト")
    total: int = Field(..., description="総検索結果数")
