from .log import logger as logger

"""
日志模块的初始化文件
作用：
1. 导出logger对象,使其可以通过 'from app.log import logger' 方式导入
2. 简化日志对象的导入路径
3. 统一项目的日志入口

使用示例：
from app.log import logger

logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
"""
