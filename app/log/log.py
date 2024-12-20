import sys
from loguru import logger as loguru_logger
from app.core.config import settings

class Loggin:
    """
    日志配置类
    用于设置和初始化项目的日志系统
    """
    def __init__(self) -> None:
        """
        初始化日志级别
        根据settings中的DEBUG配置决定日志级别:
        - DEBUG=True: 使用DEBUG级别,输出所有日志
        - DEBUG=False: 使用INFO级别只输出信息、警告和错误日志
        """
        debug = settings.DEBUG
        if debug:
            self.level = "DEBUG"  # 调试模式：显示所有日志
        else:
            self.level = "INFO"   # 生产模式：只显示信息及以上级别的日志

    def setup_logger(self):
        """
        配置日志系统
        1. 移除默认的日志处理器
        2. 添加新的日志处理器，将日志输出到标准输出(控制台)
        3. 设置日志级别
        
        Returns:
            loguru.logger: 配置好的logger对象
        
        注释:可以通过取消注释logger.add行来启用文件日志
        """
        loguru_logger.remove()  # 移除默认处理器
        loguru_logger.add(
            settings.LOGS_ROOT, # 设置日志文件路径
            sink=sys.stdout,    # 输出到标准输出
            level=self.level,    # 设置日志级别
            rotation="100 MB"   # 设置日志文件大小为100MB
        )
        
        # 文件日志配置示例
        # logger.add("my_project.log", level=level, rotation="100 MB")  # 输出日志到文件，当文件达到100MB时轮转

        return loguru_logger

# 创建日志配置实例
loggin = Loggin()
# 初始化并获取logger对象
logger = loggin.setup_logger()
