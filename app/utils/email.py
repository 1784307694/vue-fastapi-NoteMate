from fastapi import  HTTPException
from pydantic import BaseModel, EmailStr
import aiosmtplib
from email.message import EmailMessage
from email.utils import formataddr
import asyncio
from typing import Optional

from app.core.config import settings

# SMTP 客户端单例
_smtp_client: Optional[aiosmtplib.SMTP] = None
_smtp_lock = asyncio.Lock()

async def get_smtp_client() -> aiosmtplib.SMTP:
    """获取或创建 SMTP 客户端单例"""
    global _smtp_client
    
    if _smtp_client is None:
        async with _smtp_lock:
            if _smtp_client is None:
                # 创建新的 SMTP 客户端
                _smtp_client = aiosmtplib.SMTP(
                    hostname=settings.SMTP_SERVER,
                    port=settings.SMTP_PORT,
                    use_tls=True
                )
                await _smtp_client.connect()
                await _smtp_client.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
    
    # 检查连接是否有效, 如果无效则重新连接
    try:
        await _smtp_client.noop()
    except Exception:
        async with _smtp_lock:
            _smtp_client = aiosmtplib.SMTP(
                hostname=settings.SMTP_SERVER,
                port=settings.SMTP_PORT,
                use_tls=True
            )
            await _smtp_client.connect()
            await _smtp_client.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
    
    return _smtp_client

# 定义请求体模型
class EmailRequest(BaseModel):
    to_email: EmailStr  # 收件人邮箱
    subject: str  # 邮件主题
    body: str  # 邮件内容

# 发送邮件的函数
async def send_email(to_email: str, subject: str, body: str):
    # 创建邮件对象
    message = EmailMessage()
    # 设置发件人显示名称和邮箱地址
    message["From"] = formataddr(("Notemate", settings.SMTP_USERNAME))
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        smtp = await get_smtp_client()
        await smtp.send_message(message)
    except Exception as e:
        # 如果发送失败, 清除客户端以便下次重新创建
        global _smtp_client
        _smtp_client = None
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


