from fastapi.exceptions import (
    HTTPException,
    RequestValidationError,
    ResponseValidationError,
)
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from tortoise.exceptions import DoesNotExist, IntegrityError


class SettingNotFound(Exception):
    pass


async def DoesNotExistHandle(req: Request, exc: DoesNotExist) -> JSONResponse:
    """
    处理 DoesNotExist 异常:
    当查询数据库时，对象不存在时抛出该异常

    Args:
        req: HTTP请求对象
        exc: 异常实例
    
    Returns:
        返回404状态的JSON响应
    """
    content = dict(
        code=404,
        msg=f"Object has not found, exc: {exc}, query_params: {req.query_params}",
    )
    return JSONResponse(content=content, status_code=404)


async def IntegrityHandle(_: Request, exc: IntegrityError) -> JSONResponse:
    """
    处理数据库完整性错误(如唯一约束冲突)
    
    Args:
        _: 未使用的请求对象
        exc: 异常实例
    
    Returns:
        返回500状态的JSON响应
    """
    content = dict(
        code=500,
        msg=f"IntegrityError，{exc}",
    )
    return JSONResponse(content=content, status_code=500)


async def HttpExcHandle(_: Request, exc: HTTPException) -> JSONResponse:
    """
    处理通用HTTP异常

    处理HTTP异常，如401、403、404等
    Args:
        _: 未使用的请求对象
        exc: HTTP异常实例
    
    Returns:
        返回对应状态码的JSON响应
    """
    content = dict(code=exc.status_code, msg=exc.detail, data=None)
    return JSONResponse(content=content, status_code=exc.status_code)


async def RequestValidationHandle(_: Request, exc: RequestValidationError) -> JSONResponse:
    """
    处理请求数据验证失败的异常

    Args:
        _: 未使用的请求对象
        exc: 验证错误异常实例
    
    Returns:
        返回422状态的JSON响应
    """
    content = dict(code=422, msg=f"RequestValidationError, {exc}")
    return JSONResponse(content=content, status_code=422)


async def ResponseValidationHandle(_: Request, exc: ResponseValidationError) -> JSONResponse:
    """
    处理响应数据验证失败的异常
    
    Args:
        _: 未使用的请求对象
        exc: 验证错误异常实例
    
    Returns:
        返回500状态的JSON响应
    """
    content = dict(code=500, msg=f"ResponseValidationError, {exc}")
    return JSONResponse(content=content, status_code=500)
