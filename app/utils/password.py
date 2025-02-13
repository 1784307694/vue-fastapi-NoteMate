from passlib import pwd
from passlib.context import CryptContext

# 创建密码加密上下文,使用argon2算法
# argon2是一个强密码哈希算法,获得过密码哈希竞赛冠军
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否正确
    
    Args:
        plain_password: 明文密码
        hashed_password: 已加密的密码哈希值
        
    Returns:
        bool: 如果密码匹配返回True,否则返回False
        
    说明:
        - 使用passlib内置的verify方法进行密码验证
        - 会自动处理不同加密算法的兼容性
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    对密码进行加密
    
    Args:
        password: 需要加密的明文密码
        
    Returns:
        str: 返回加密后的密码哈希值
        
    说明:
        - 使用argon2算法进行加密
        - 会自动生成随机盐值(salt)
        - 生成的哈希值已包含算法信息,可直接用于验证
    """
    return pwd_context.hash(password)


def generate_password() -> str:
    """
    生成随机密码
    
    Returns:
        str: 返回生成的随机密码
        
    说明:
        - 使用passlib的pwd模块生成随机密码
        - 生成的密码符合一定的复杂度要求
        - 主要用于系统自动生成初始密码
    """
    return pwd.genword()
