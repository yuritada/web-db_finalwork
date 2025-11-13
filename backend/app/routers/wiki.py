"""
Wiki API endpoints (v3)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.connect import get_session
from app.db.create import create_wiki_page, share_wiki_page
from app.db.read import get_wiki_pages_for_user, get_wiki_page_by_id
from app.db.update import update_wiki_page
from app.db.delete import remove_wiki_permission
from app.core.dependencies import (
    get_current_user,
    check_wiki_view_permission,
    check_wiki_edit_permission
)
from app.models.user import User
from app.schemas.wiki import (
    WikiPageCreate,
    WikiPageUpdate,
    WikiPagePublic,
    WikiPageDetail,
    PermissionSet
)

router = APIRouter(prefix="/wiki", tags=["Wiki"])


@router.get("/pages", response_model=List[WikiPagePublic])
async def get_wiki_pages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    ユーザーが閲覧権限を持つWikiページ一覧を取得

    Args:
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        List[WikiPagePublic]: Wikiページ一覧
    """
    pages = get_wiki_pages_for_user(db, current_user.id)
    return pages


@router.post("/pages", response_model=WikiPagePublic, status_code=status.HTTP_201_CREATED)
async def create_new_wiki_page(
    page_data: WikiPageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    新規Wikiページを作成

    作成者に自動的にEDIT権限が付与されます

    Args:
        page_data: ページ作成データ
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        WikiPagePublic: 作成されたページ
    """
    new_page = create_wiki_page(db, page_data, current_user.id)
    return new_page


@router.get("/pages/{page_id}", response_model=WikiPageDetail)
async def get_wiki_page(
    page_id: int,
    current_user: User = Depends(check_wiki_view_permission),
    db: Session = Depends(get_session)
):
    """
    Wikiページの詳細を取得

    閲覧権限（VIEW_ONLY以上）が必要

    Args:
        page_id: WikiページID
        current_user: 認証済み・権限チェック済みユーザー
        db: データベースセッション

    Returns:
        WikiPageDetail: ページ詳細（権限情報含む）

    Raises:
        HTTPException: ページが存在しない場合（404）
    """
    page = get_wiki_page_by_id(db, page_id)

    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wiki page not found"
        )

    return page


@router.put("/pages/{page_id}", response_model=WikiPagePublic)
async def update_existing_wiki_page(
    page_id: int,
    page_update: WikiPageUpdate,
    current_user: User = Depends(check_wiki_edit_permission),
    db: Session = Depends(get_session)
):
    """
    Wikiページを更新

    編集権限（EDIT）が必要

    Args:
        page_id: WikiページID
        page_update: 更新データ
        current_user: 認証済み・権限チェック済みユーザー
        db: データベースセッション

    Returns:
        WikiPagePublic: 更新されたページ

    Raises:
        HTTPException: ページが存在しない場合（404）
    """
    updated_page = update_wiki_page(db, page_id, page_update)

    if not updated_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wiki page not found"
        )

    return updated_page


@router.post("/pages/{page_id}/share", status_code=status.HTTP_201_CREATED)
async def share_wiki_page_with_user(
    page_id: int,
    permission_data: PermissionSet,
    current_user: User = Depends(check_wiki_edit_permission),
    db: Session = Depends(get_session)
):
    """
    Wikiページの権限を他のユーザーに付与

    編集権限（EDIT）が必要

    Args:
        page_id: WikiページID
        permission_data: 権限設定データ
        current_user: 認証済み・権限チェック済みユーザー
        db: データベースセッション

    Returns:
        dict: 成功メッセージ

    Raises:
        HTTPException: ページが存在しない場合（404）
    """
    # ページの存在確認
    page = get_wiki_page_by_id(db, page_id)
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wiki page not found"
        )

    # 権限を付与
    share_wiki_page(
        db,
        page_id,
        permission_data.user_id,
        permission_data.permission_level
    )

    return {"success": True}


@router.delete("/pages/{page_id}/share/{user_id}", status_code=status.HTTP_200_OK)
async def unshare_wiki_page_from_user(
    page_id: int,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Wikiページの共有を解除（権限削除）

    作成者のみが実行可能

    Args:
        page_id: WikiページID
        user_id: 権限を削除するユーザーのID（UUID文字列）
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        dict: 成功メッセージ

    Raises:
        HTTPException: ページが存在しない場合（404）、作成者でない場合（403）、権限が存在しない場合（404）
    """
    import uuid as uuid_lib

    # ページの存在確認
    page = get_wiki_page_by_id(db, page_id)
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wiki page not found"
        )

    # 作成者チェック（Wikiの作成者のみが共有解除可能）
    if page.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator can unshare this wiki page"
        )

    # UUIDに変換
    try:
        target_user_id = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    # 権限を削除
    success = remove_wiki_permission(db, page_id, target_user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found for this user"
        )

    return {"success": True}
