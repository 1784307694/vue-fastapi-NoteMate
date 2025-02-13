from jose import jwt

from app.schemas.login import JWTPayload
from app.core.config import settings


def create_access_token(*, data: JWTPayload):
    """
    创建访问令牌
    
    Args:
        data: JWT载荷数据
        
    Returns:
        str: 编码后的JWT令牌
    """
    # 将数据转换为字典并copy一份避免改动源数据
    payload = data.model_dump().copy()
    # 解码
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt