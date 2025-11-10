"""
UPDATE operations (v3)
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.models.wiki import WikiPage
from app.schemas.wiki import WikiPageUpdate


def update_wiki_page(
    db: Session,
    page_id: int,
    page_update: WikiPageUpdate
) -> Optional[WikiPage]:
    """
    Wikiページを更新する

    Args:
        db: データベースセッション
        page_id: WikiページID
        page_update: 更新内容

    Returns:
        更新されたWikiPage、または存在しない場合はNone
    """
    # ページを取得
    db_page = db.query(WikiPage).filter(WikiPage.id == page_id).first()

    if not db_page:
        return None

    # 更新データを適用（Noneでないフィールドのみ）
    if page_update.title is not None:
        db_page.title = page_update.title

    if page_update.content is not None:
        db_page.content = page_update.content

    # updated_atは自動更新されるが、明示的に設定することも可能
    db_page.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_page)

    return db_page
