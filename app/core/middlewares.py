import re
from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.dependency import AuthControl
from app.models.admin import AuditLog, User

from .bgtask import BgTasks


class SimpleBaseMiddleware:
    """
    简单中间件基类
    提供请求前后处理的基本框架
    """
    def __init__(self, app: ASGIApp) -> None:
        """
        初始化中间件
        Args:
            app: ASGI应用实例
        """
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        中间件调用方法,处理每个请求
        Args:
            scope: ASGI作用域,包含请求的基本信息
            receive: 用于接收请求体的异步函数
            send: 用于发送响应的异步函数
        """
        # 如果不是HTTP请求,直接交给下一个中间件处理
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 创建请求对象
        request = Request(scope, receive=receive)

        # 执行请求前处理,如果before_request没有返回值则使用self.app
        response = await self.before_request(request) or self.app
        # 处理请求
        await response(request.scope, request.receive, send)
        # 执行请求后处理
        await self.after_request(request)

    async def before_request(self, request: Request):
        """请求前处理钩子方法"""
        return self.app

    async def after_request(self, request: Request):
        """请求后处理钩子方法"""
        return None


class BackGroundTaskMiddleware(SimpleBaseMiddleware):
    """
    后台任务中间件
    用于处理异步任务的初始化和执行
    """
    async def before_request(self, request):
        """请求前初始化后台任务对象"""
        await BgTasks.init_bg_tasks_obj()

    async def after_request(self, request):
        """请求后执行后台任务"""
        await BgTasks.execute_tasks()


class HttpAuditLogMiddleware(BaseHTTPMiddleware):
    """
    HTTP审计日志中间件
    记录API请求的详细信息,用于系统审计
    """
    def __init__(self, app, methods: list, exclude_paths: list):
        """
        初始化审计日志中间件
        Args:
            app: FastAPI应用实例
            methods: 需要记录的HTTP方法列表
            exclude_paths: 不需要记录日志的路径列表
        """
        super().__init__(app)
        self.methods = methods
        self.exclude_paths = exclude_paths

    async def get_request_log(self, request: Request, response: Response) -> dict:
        """
        获取请求日志信息
        Args:
            request: 请求对象
            response: 响应对象
        Returns:
            dict: 包含请求详细信息的字典
        """
        # 获取客户端真实IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # 如果有代理，取第一个IP
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            # 否则获取直接的客户端IP
            client_ip = request.client.host if request.client else None
        
        # 基本请求信息
        data: dict = {
            "path": request.url.path,           # 请求路径
            "status": response.status_code,     # 响应状态码
            "method": request.method,           # 请求方法
            "ip": client_ip,                    # 客户端IP地址
        }

        # 获取路由信息(API标签和描述)
        app: FastAPI = request.app
        for route in app.routes:
            if (
                isinstance(route, APIRoute)  # 确保是API路由
                and route.path_regex.match(request.url.path)  # 路径匹配
                and request.method in route.methods  # 方法匹配
            ):
                data["module"] = ",".join(route.tags)  # API模块标签
                data["summary"] = route.summary       # API描述

        # 获取用户信息
        try:
            token = request.headers.get("token")
            user_obj = None
            if token:
                user_obj: User = await AuthControl.is_authed(token)
            # 记录用户ID和用户名
            data["user_id"] = user_obj.id if user_obj else 0
            data["username"] = user_obj.username if user_obj else ""
        except Exception as e:
            # 获取用户信息失败时设置默认值
            data["user_id"] = 0
            data["username"] = ""
        return data

    async def before_request(self, request: Request):
        """请求前处理(此处未使用)"""
        pass

    async def after_request(self, request: Request, response: Response, process_time: int):
        """
        请求后处理：记录审计日志
        Args:
            request: 请求对象
            response: 响应对象
            process_time: 请求处理时间(毫秒)
        """
        # 检查是否需要记录该请求
        if request.method in self.methods:  # 请求方法符合记录要求
            # 检查是否在排除路径中
            for path in self.exclude_paths:
                if re.search(path, request.url.path, re.I) is not None:
                    return
                
            # 获取日志数据并记录
            data: dict = await self.get_request_log(request=request, response=response)
            data["response_time"] = process_time  # 添加响应时间
            await AuditLog.create(**data)  # 创建审计日志记录

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        中间件调度方法
        Args:
            request: 请求对象
            call_next: 下一个处理函数
        Returns:
            Response: 响应对象
        """
        # 记录请求开始时间
        start_time: datetime = datetime.now()
        
        # 请求前处理
        await self.before_request(request)

        # 在请求处理前的逻辑
        # 处理请求
        response = await call_next(request)
        # 在响应返回前的逻辑
        
        # 计算请求处理时间(毫秒)
        end_time: datetime = datetime.now()
        process_time = int((end_time.timestamp() - start_time.timestamp()) * 1000)
        
        # 请求后处理(记录日志)
        await self.after_request(request, response, process_time)
        
        return response
