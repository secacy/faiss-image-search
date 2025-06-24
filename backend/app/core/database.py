"""
数据库连接和操作模块
使用SQLAlchemy进行数据库操作
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import asyncio
from contextlib import asynccontextmanager

from .config import get_settings

# 获取配置
settings = get_settings()

# 创建数据库引擎
engine = create_engine(
    settings.database.url,
    poolclass=QueuePool,
    pool_size=settings.database.pool_size,
    pool_recycle=settings.database.pool_recycle,
    pool_pre_ping=True,
    echo=settings.server.debug
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

# 元数据对象
metadata = MetaData()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话
    用于依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def get_async_db():
    """异步数据库会话上下文管理器"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def create_tables():
    """创建数据库表"""
    try:
        # 导入所有模型以确保它们被注册
        from ..models import user, image, faiss_index, operation_log
        
        # 在单独的线程中运行数据库表创建
        def _create_tables():
            Base.metadata.create_all(bind=engine)
        
        # 使用线程池执行阻塞操作
        await asyncio.get_event_loop().run_in_executor(None, _create_tables)
        print("✅ 数据库表创建完成")
    except Exception as e:
        print(f"❌ 数据库表创建失败: {e}")
        raise


def check_database_connection() -> bool:
    """检查数据库连接状态"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = SessionLocal
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.session_factory()
    
    @asynccontextmanager
    async def get_async_session(self):
        """异步获取数据库会话"""
        session = self.session_factory()
        try:
            yield session
        finally:
            session.close()
    
    def execute_raw_sql(self, sql: str, params: dict = None):
        """执行原生SQL"""
        with self.engine.connect() as conn:
            return conn.execute(sql, params or {})
    
    def check_connection(self) -> bool:
        """检查数据库连接"""
        return check_database_connection()


# 全局数据库管理器实例
db_manager = DatabaseManager() 