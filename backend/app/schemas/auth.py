"""
Authentication schemas (v3)
"""
from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    """OAuth2準拠のログインリクエスト"""
    username: str = Field(..., description="ユーザー名")
    password: str = Field(..., description="パスワード")
    grant_type: str = Field(default="password", description="OAuth2 grant type")
    scope: str = Field(default="", description="OAuth2 scope")
    client_id: str | None = Field(None, description="OAuth2 client ID")
    client_secret: str | None = Field(None, description="OAuth2 client secret")

    model_config = {"extra": "allow"}
