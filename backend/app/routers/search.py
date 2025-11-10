"""
Search API endpoints (v3)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Literal, List

from app.db.connect import get_session
from app.db.read import search_wiki_pages, search_tags, search_users
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.search import SearchResponse, SearchResult

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="検索キーワード"),
    type: Literal["wiki", "tag", "user", "all"] = Query(
        default="all",
        description="検索対象タイプ"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    統合検索エンドポイント

    検索対象:
    - wiki: Wikiページのタイトルと本文（権限チェック付き）
    - tag: タグ名
    - user: ユーザー名とメールアドレス
    - all: 上記すべて（デフォルト）

    検索方式: 部分一致（大文字小文字区別なし）

    Args:
        q: 検索キーワード
        type: 検索対象タイプ
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        SearchResponse: 検索結果リスト
    """
    results: List[SearchResult] = []

    # Wikiページ検索
    if type in ["wiki", "all"]:
        wiki_pages = search_wiki_pages(db, q, current_user.id)
        for page in wiki_pages:
            # snippetは本文の最初の200文字を抽出
            snippet = page.content[:200] + "..." if len(page.content) > 200 else page.content
            results.append(SearchResult(
                type="wiki",
                id=page.id,
                title=page.title,
                snippet=snippet
            ))

    # タグ検索
    if type in ["tag", "all"]:
        tags = search_tags(db, q)
        for tag in tags:
            results.append(SearchResult(
                type="tag",
                id=tag.id,
                name=tag.name
            ))

    # ユーザー検索
    if type in ["user", "all"]:
        users = search_users(db, q)
        for user in users:
            results.append(SearchResult(
                type="user",
                id=str(user.id),  # UUIDを文字列に変換
                username=user.username,
                email=user.email
            ))

    return SearchResponse(
        results=results,
        total=len(results)
    )
