"""
Wiki permissions tests (Wiki権限詳細テスト)

Tests for:
- VIEW_ONLY permission (閲覧のみ権限)
- EDIT permission (編集権限)
- Creator permissions (作成者権限)
- Permission sharing (権限共有)
"""
import pytest
from fastapi import status


def test_wiki_create_success(authenticated_client, test_user):
    """Wikiページ作成成功"""
    response = authenticated_client.post(
        "/wiki/pages",
        json={
            "title": "Test Wiki Page",
            "content": "This is a test wiki page content."
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Test Wiki Page"
    assert data["content"] == "This is a test wiki page content."
    assert str(data["creator_id"]) == str(test_user.id)


def test_wiki_creator_can_always_edit(client, db, test_user):
    """作成者は常にWiki編集可能"""
    # Login as test_user
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    # Create wiki page
    create_response = client.post(
        "/wiki/pages",
        json={"title": "Creator Test", "content": "Original content"}
    )
    page_id = create_response.json()["id"]

    # Update own wiki page
    update_response = client.put(
        f"/wiki/pages/{page_id}",
        json={"title": "Creator Test Updated", "content": "Updated content"}
    )

    assert update_response.status_code == status.HTTP_200_OK
    data = update_response.json()
    assert data["title"] == "Creator Test Updated"
    assert data["content"] == "Updated content"


def test_wiki_view_only_can_view(client, db, test_user, other_user):
    """VIEW_ONLY権限で閲覧可能"""
    # Login as test_user and create page
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/wiki/pages",
        json={"title": "Shared Page", "content": "Shared content"}
    )
    page_id = create_response.json()["id"]

    # Share with other_user (VIEW_ONLY)
    share_response = client.post(
        f"/wiki/pages/{page_id}/share",
        json={
            "user_id": str(other_user.id),
            "permission_level": "VIEW_ONLY"
        }
    )
    assert share_response.status_code == status.HTTP_201_CREATED

    # Login as other_user and try to view
    login_response2 = client.post(
        "/auth/token",
        data={"username": other_user.username, "password": other_user.plain_password}
    )
    token2 = login_response2.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token2}"}

    view_response = client.get(f"/wiki/pages/{page_id}")

    assert view_response.status_code == status.HTTP_200_OK
    data = view_response.json()
    assert data["title"] == "Shared Page"


def test_wiki_view_only_cannot_edit(client, db, test_user, other_user):
    """VIEW_ONLY権限ではWiki編集不可"""
    # Login as test_user and create page
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/wiki/pages",
        json={"title": "Edit Test Page", "content": "Original"}
    )
    page_id = create_response.json()["id"]

    # Share with other_user (VIEW_ONLY)
    client.post(
        f"/wiki/pages/{page_id}/share",
        json={
            "user_id": str(other_user.id),
            "permission_level": "VIEW_ONLY"
        }
    )

    # Login as other_user and try to edit
    login_response2 = client.post(
        "/auth/token",
        data={"username": other_user.username, "password": other_user.plain_password}
    )
    token2 = login_response2.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token2}"}

    edit_response = client.put(
        f"/wiki/pages/{page_id}",
        json={"title": "Edited Title", "content": "Edited content"}
    )

    assert edit_response.status_code == status.HTTP_403_FORBIDDEN


def test_wiki_edit_permission_can_edit(client, db, test_user, other_user):
    """EDIT権限ではWiki編集可能"""
    # Login as test_user and create page
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/wiki/pages",
        json={"title": "Editable Page", "content": "Original"}
    )
    page_id = create_response.json()["id"]

    # Share with other_user (EDIT)
    client.post(
        f"/wiki/pages/{page_id}/share",
        json={
            "user_id": str(other_user.id),
            "permission_level": "EDIT"
        }
    )

    # Login as other_user and edit
    login_response2 = client.post(
        "/auth/token",
        data={"username": other_user.username, "password": other_user.plain_password}
    )
    token2 = login_response2.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token2}"}

    edit_response = client.put(
        f"/wiki/pages/{page_id}",
        json={"title": "Edited by Other", "content": "New content"}
    )

    assert edit_response.status_code == status.HTTP_200_OK
    data = edit_response.json()
    assert data["title"] == "Edited by Other"
    assert data["content"] == "New content"


def test_wiki_share_requires_edit_permission(client, db, test_user, other_user):
    """Wiki共有にはEDIT権限が必要"""
    # Login as test_user and create page
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/wiki/pages",
        json={"title": "Share Test", "content": "Content"}
    )
    page_id = create_response.json()["id"]

    # Share with other_user (VIEW_ONLY)
    client.post(
        f"/wiki/pages/{page_id}/share",
        json={
            "user_id": str(other_user.id),
            "permission_level": "VIEW_ONLY"
        }
    )

    # Login as other_user (VIEW_ONLY permission)
    login_response2 = client.post(
        "/auth/token",
        data={"username": other_user.username, "password": other_user.plain_password}
    )
    token2 = login_response2.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token2}"}

    # Try to share with another user (should fail - VIEW_ONLY cannot share)
    # Create a third user for this test
    client.post(
        "/auth/signup",
        json={
            "username": "thirduser",
            "email": "third@example.com",
            "password": "ThirdPass123!",
            "kategori": "学生",
            "gakuseki_bango": "THIRD01",
            "faculty": "工学部"
        }
    )
    third_user_response = client.post(
        "/auth/token",
        data={"username": "thirduser", "password": "ThirdPass123!"}
    )
    third_user_id = client.get("/users/me", headers={"Authorization": f"Bearer {third_user_response.json()['access_token']}"}).json()["id"]

    # Switch back to other_user
    client.headers = {"Authorization": f"Bearer {token2}"}

    share_response = client.post(
        f"/wiki/pages/{page_id}/share",
        json={
            "user_id": third_user_id,
            "permission_level": "VIEW_ONLY"
        }
    )

    assert share_response.status_code == status.HTTP_403_FORBIDDEN


def test_wiki_no_permission_cannot_view(client, db, test_user, other_user):
    """権限なしではWiki閲覧不可"""
    # Login as test_user and create page (without sharing)
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/wiki/pages",
        json={"title": "Private Page", "content": "Private content"}
    )
    page_id = create_response.json()["id"]

    # Login as other_user (no permission granted)
    login_response2 = client.post(
        "/auth/token",
        data={"username": other_user.username, "password": other_user.plain_password}
    )
    token2 = login_response2.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token2}"}

    view_response = client.get(f"/wiki/pages/{page_id}")

    assert view_response.status_code == status.HTTP_403_FORBIDDEN


def test_wiki_list_shows_only_accessible_pages(client, db, test_user, other_user):
    """Wikiページ一覧は権限のあるページのみ表示"""
    # Login as test_user
    login_response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": test_user.plain_password}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}

    # Create two pages
    client.post("/wiki/pages", json={"title": "Page 1", "content": "Content 1"})
    create_response2 = client.post("/wiki/pages", json={"title": "Page 2", "content": "Content 2"})
    page2_id = create_response2.json()["id"]

    # Share only Page 2 with other_user
    client.post(
        f"/wiki/pages/{page2_id}/share",
        json={
            "user_id": str(other_user.id),
            "permission_level": "VIEW_ONLY"
        }
    )

    # Login as other_user
    login_response2 = client.post(
        "/auth/token",
        data={"username": other_user.username, "password": other_user.plain_password}
    )
    token2 = login_response2.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token2}"}

    # Get wiki pages list
    list_response = client.get("/wiki/pages")

    assert list_response.status_code == status.HTTP_200_OK
    pages = list_response.json()
    # other_user should only see Page 2
    assert len(pages) == 1
    assert pages[0]["title"] == "Page 2"
