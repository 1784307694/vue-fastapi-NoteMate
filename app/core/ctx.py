import contextvars
from starlette.background import BackgroundTasks

# 用户ID上下文变量
# 用于在整个请求生命周期中传递当前用户ID
# default=0 表示默认值为0(未登录/匿名用户)  
CTX_USER_ID: contextvars.ContextVar[int] = contextvars.ContextVar("user_id", default=0)

# 后台任务上下文变量
# 用于存储当前请求的后台任务队列
# default=None 表示默认没有后台任务
CTX_BG_TASKS: contextvars.ContextVar[BackgroundTasks] = contextvars.ContextVar("bg_task", default=None)
