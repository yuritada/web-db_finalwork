"""
Token schemas (v3)
"""
from pydantic import BaseModel


class Token(BaseModel):
    """JWT トークンレスポンス"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """JWT トークンペイロード"""
    username: str | None = None
