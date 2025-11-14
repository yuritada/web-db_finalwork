"""
Tag API endpoints (v3)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.connect import get_session
from app.db.create import create_tag, assign_tag_to_user
from app.db.read import get_all_tags, get_tags_for_user, get_tag_by_id, get_user_by_id
from app.db.delete import delete_tag, remove_tag_assignment
from app.core.dependencies import (
    get_current_user,
    check_tag_assign_permission
)
from app.models.user import User
from app.schemas.tag import (
    TagCreate,
    TagPublic,
    TagDetail,
    TagAssignment,
    UserInfo
)

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("", response_model=List[TagPublic])
async def get_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    すべてのタグ一覧を取得

    v3仕様書: GET /tags
    全ユーザーがすべてのタグを閲覧可能

    Args:
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        List[TagPublic]: タグ一覧（作成者のユーザー名を含む）
    """
    tags = get_all_tags(db)

    # 各タグに作成者のユーザー名を追加
    result = []
    for tag in tags:
        creator = get_user_by_id(db, tag.creator_id)
        result.append(TagPublic(
            id=tag.id,
            name=tag.name,
            creator_id=tag.creator_id,
            creator_username=creator.username if creator else "Unknown"
        ))

    return result


@router.post("", response_model=TagPublic, status_code=status.HTTP_201_CREATED)
async def create_new_tag(
    tag_data: TagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    新規タグを作成

    作成者のcreator_idが自動的に記録されます

    Args:
        tag_data: タグ作成データ
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        TagPublic: 作成されたタグ

    Raises:
        HTTPException: タグ名が既に存在する場合（400）
    """
    # タグ名の重複チェックは DBの unique 制約で行われる
    try:
        new_tag = create_tag(db, tag_data, current_user.id)
        return TagPublic(
            id=new_tag.id,
            name=new_tag.name,
            creator_id=new_tag.creator_id,
            creator_username=current_user.username
        )
    except Exception as e:
        # unique constraint violation
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag name already exists"
            )
        raise


@router.get("/{tag_id}", response_model=TagDetail)
async def get_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    タグの詳細を取得（割り当てられたユーザー一覧含む）

    Args:
        tag_id: タグID
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        TagDetail: タグ詳細（割り当てられたユーザーリスト含む）

    Raises:
        HTTPException: タグが存在しない場合（404）
    """
    tag = get_tag_by_id(db, tag_id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    # 割り当てられたユーザーを取得
    assigned_users = [
        UserInfo(
            id=user_tag.user.id,
            username=user_tag.user.username,
            email=user_tag.user.email
        )
        for user_tag in tag.user_tags
    ]

    # TagDetailを構築
    tag_detail = TagDetail(
        id=tag.id,
        name=tag.name,
        creator_id=tag.creator_id,
        assigned_users=assigned_users
    )

    return tag_detail


@router.post("/{tag_id}/assign", status_code=status.HTTP_201_CREATED)
async def assign_tag(
    tag_id: int,
    assignment_data: TagAssignment,
    current_user: User = Depends(check_tag_assign_permission),
    db: Session = Depends(get_session)
):
    """
    ユーザーにタグを割り当てる

    【v3権限ロジック】
    - 学生: 誰にでもタグ割り当て可能
    - 教員: 自分が作成したタグのみ割り当て可能

    Args:
        tag_id: タグID
        assignment_data: 割り当てデータ（user_id）
        current_user: 認証済み・権限チェック済みユーザー
        db: データベースセッション

    Returns:
        dict: 成功メッセージ

    Raises:
        HTTPException: ユーザーが存在しない場合（404）
    """
    # ユーザーの存在確認
    target_user = get_user_by_id(db, assignment_data.user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # タグを割り当て
    assign_tag_to_user(db, tag_id, assignment_data.user_id)

    return {"success": True}


@router.delete("/{tag_id}/assign/{user_id}", status_code=status.HTTP_200_OK)
async def unassign_tag_from_user(
    tag_id: int,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    タグの割り当てを解除

    タグの作成者のみが実行可能

    Args:
        tag_id: タグID
        user_id: 割り当てを解除するユーザーのID（UUID文字列）
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        dict: 成功メッセージ

    Raises:
        HTTPException: タグが存在しない場合（404）、作成者でない場合（403）、割り当てが存在しない場合（404）
    """
    import uuid as uuid_lib

    # タグの存在確認
    tag = get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    # 作成者チェック（タグの作成者のみが割り当て解除可能）
    if tag.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator can unassign this tag"
        )

    # UUIDに変換
    try:
        target_user_id = uuid_lib.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    # 割り当てを解除
    success = remove_tag_assignment(db, tag_id, target_user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag assignment not found for this user"
        )

    return {"success": True}


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag_endpoint(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    タグを削除（作成者のみ）

    Args:
        tag_id: タグID
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        None（204 No Content）

    Raises:
        HTTPException: タグが存在しない場合（404）、権限がない場合（403）
    """
    # タグの存在確認
    tag = get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    # 作成者チェック
    if tag.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete tags that you created"
        )

    # タグを削除
    delete_tag(db, tag_id)

    return None
