"""
配置管理模块
负责加载和管理应用配置
"""

import os
import yaml
from typing import List, Optional
from pydantic import BaseModel
from functools import lru_cache


class ServerConfig(BaseModel):
    """服务器配置"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    cors_origins: List[str] = ["http://localhost:3000"]


class DatabaseConfig(BaseModel):
    """数据库配置"""
    host: str = "localhost"
    port: int = 3306
    username: str = "root"
    password: str = "password"
    database: str = "pic_search"
    charset: str = "utf8mb4"
    pool_size: int = 10
    pool_recycle: int = 3600

    @property
    def url(self) -> str:
        """获取数据库连接URL"""
        return f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?charset={self.charset}"


class StorageConfig(BaseModel):
    """文件存储配置"""
    upload_dir: str = "data\\images"
    max_file_size: int = 10485760  # 10MB
    allowed_extensions: List[str] = ["jpg", "jpeg", "png", "bmp", "webp"]
    thumbnail_size: List[int] = [256, 256]


class FaissConfig(BaseModel):
    """Faiss索引配置"""
    index_path: str = "data\\index\\image_features.index"
    feature_dim: int = 2048
    index_type: str = "IndexFlatIP"
    nprobe: int = 10


class ModelConfig(BaseModel):
    """模型配置"""
    name: str = "resnet50"
    pretrained: bool = True
    device: str = "cuda"
    batch_size: int = 32


class AuthConfig(BaseModel):
    """认证配置"""
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "logs/app.log"
    max_size: int = 10485760
    backup_count: int = 5


class SearchConfig(BaseModel):
    """搜索配置"""
    default_k: int = 10
    max_k: int = 100
    similarity_threshold: float = 0.5


class AdminConfig(BaseModel):
    """管理员配置"""
    default_username: str = "admin"
    default_password: str = "admin123"


class Settings(BaseModel):
    """应用设置"""
    server: ServerConfig = ServerConfig()
    database: DatabaseConfig = DatabaseConfig()
    storage: StorageConfig = StorageConfig()
    faiss: FaissConfig = FaissConfig()
    model: ModelConfig = ModelConfig()
    auth: AuthConfig = AuthConfig()
    logging: LoggingConfig = LoggingConfig()
    search: SearchConfig = SearchConfig()
    admin: AdminConfig = AdminConfig()


def load_config_from_yaml(config_path: str = "..\\config\\config.yaml") -> dict:
    """从YAML文件加载配置"""
    try:
        # 尝试相对路径和绝对路径
        possible_paths = [
            config_path,
            os.path.join(os.getcwd(), config_path),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), config_path)
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
        
        print(f"⚠️  配置文件未找到: {config_path}，使用默认配置")
        return {}
    except Exception as e:
        print(f"⚠️  加载配置文件失败: {e}，使用默认配置")
        return {}


@lru_cache()
def get_settings() -> Settings:
    """获取应用设置（带缓存）"""
    # 加载YAML配置
    yaml_config = load_config_from_yaml()
    
    # 创建配置对象
    config_dict = {}
    
    # 解析各个配置段
    if 'server' in yaml_config:
        config_dict['server'] = ServerConfig(**yaml_config['server'])
    
    if 'database' in yaml_config:
        config_dict['database'] = DatabaseConfig(**yaml_config['database'])
    
    if 'storage' in yaml_config:
        config_dict['storage'] = StorageConfig(**yaml_config['storage'])
    
    if 'faiss' in yaml_config:
        config_dict['faiss'] = FaissConfig(**yaml_config['faiss'])
    
    if 'model' in yaml_config:
        config_dict['model'] = ModelConfig(**yaml_config['model'])
    
    if 'auth' in yaml_config:
        config_dict['auth'] = AuthConfig(**yaml_config['auth'])
    
    if 'logging' in yaml_config:
        config_dict['logging'] = LoggingConfig(**yaml_config['logging'])
    
    if 'search' in yaml_config:
        config_dict['search'] = SearchConfig(**yaml_config['search'])
    
    if 'admin' in yaml_config:
        config_dict['admin'] = AdminConfig(**yaml_config['admin'])
    
    return Settings(**config_dict)


# 全局设置实例
settings = get_settings() 