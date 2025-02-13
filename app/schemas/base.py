from typing import Any, Optional

from fastapi.responses import JSONResponse


class Success(JSONResponse):
    """
    成功响应类
    继承自FastAPI的JSONResponse,用于返回成功的API响应
    """
    def __init__(
        self,
        code: int = 200,                    # 状态码,默认200
        msg: Optional[str] = "OK",          # 响应消息,默认"OK"
        data: Optional[Any] = None,         # 响应数据,默认None
        **kwargs,                           # 其他可选参数
    ):
        # 构建响应内容字典
        content = {
            "code": code,                   # 状态码
            "msg": msg,                     # 响应消息
            "data": data                    # 响应数据
        }
        # 更新其他可选参数
        content.update(kwargs)
        # 调用父类构造函数,设置响应内容和状态码
        super().__init__(content=content, status_code=code)


class Fail(JSONResponse):
    """
    失败响应类
    继承自FastAPI的JSONResponse,用于返回失败的API响应
    """
    def __init__(
        self,
        code: int = 400,                    # 状态码,默认400
        msg: Optional[str] = None,          # 错误消息
        data: Optional[Any] = None,         # 错误相关的数据
        **kwargs,                           # 其他可选参数
    ):
        # 构建响应内容字典
        content = {
            "code": code,                   # 状态码
            "msg": msg,                     # 错误消息
            "data": data                    # 错误数据
        }
        # 更新其他可选参数
        content.update(kwargs)
        # 调用父类构造函数,设置响应内容和状态码
        super().__init__(content=content, status_code=code)


class SuccessExtra(JSONResponse):
    """
    带分页信息的成功响应类
    继承自FastAPI的JSONResponse,用于返回带分页信息的API响应
    主要用于列表数据的返回
    """
    def __init__(
        self,
        code: int = 200,                    # 状态码,默认200
        msg: Optional[str] = None,          # 响应消息
        data: Optional[Any] = None,         # 响应数据
        total: int = 0,                     # 数据总数
        page: int = 1,                      # 当前页码
        page_size: int = 20,                # 每页数据量
        **kwargs,                           # 其他可选参数
    ):
        # 构建响应内容字典,包含分页信息
        content = {
            "code": code,                   # 状态码
            "msg": msg,                     # 响应消息
            "data": data,                   # 响应数据
            "total": total,                 # 数据总数
            "page": page,                   # 当前页码
            "page_size": page_size          # 每页数据量
        }
        # 更新其他可选参数
        content.update(kwargs)
        # 调用父类构造函数,设置响应内容和状态码
        super().__init__(content=content, status_code=code)
