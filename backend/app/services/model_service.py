"""
模型服务
负责加载PyTorch模型并提取图像特征
"""

import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import numpy as np
from typing import List, Union, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import io

from ..core.config import get_settings
from ..utils.logger import LoggerMixin

settings = get_settings()


class ModelService(LoggerMixin):
    """模型服务类"""
    
    def __init__(self):
        self.model = None
        self.device = None
        self.transform = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.feature_dim = settings.faiss.feature_dim
        
    async def initialize(self):
        """初始化模型"""
        try:
            self.logger.info("正在初始化图像特征提取模型...")
            
            # 设置设备
            self.device = torch.device(
                settings.model.device if torch.cuda.is_available() 
                and settings.model.device == "cuda" else "cpu"
            )
            self.logger.info(f"使用设备: {self.device}")
            
            # 在线程池中加载模型
            await asyncio.get_event_loop().run_in_executor(
                self.executor, self._load_model
            )
            
            self.logger.info("图像特征提取模型初始化完成")
            
        except Exception as e:
            self.logger.error(f"模型初始化失败: {e}")
            raise
    
    def _load_model(self):
        """加载模型（在线程池中执行）"""
        # 加载预训练的ResNet50模型
        if settings.model.name.lower() == "resnet50":
            model = models.resnet50(pretrained=settings.model.pretrained)
            # 移除最后的分类层，只保留特征提取部分
            model = nn.Sequential(*list(model.children())[:-1])
        elif settings.model.name.lower() == "resnet18":
            model = models.resnet18(pretrained=settings.model.pretrained)
            model = nn.Sequential(*list(model.children())[:-1])
        else:
            # 默认使用ResNet50
            model = models.resnet50(pretrained=settings.model.pretrained)
            model = nn.Sequential(*list(model.children())[:-1])
        
        # 设置为评估模式
        model.eval()
        model = model.to(self.device)
        
        self.model = model
        
        # 设置图像预处理
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    async def extract_features(self, image_input: Union[str, Image.Image, bytes]) -> np.ndarray:
        """
        提取图像特征
        
        Args:
            image_input: 图像输入，可以是文件路径、PIL Image对象或字节数据
            
        Returns:
            特征向量数组
        """
        try:
            # 在线程池中处理图像
            features = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._extract_features_sync, image_input
            )
            return features
        except Exception as e:
            self.logger.error(f"特征提取失败: {e}")
            raise
    
    def _extract_features_sync(self, image_input: Union[str, Image.Image, bytes]) -> np.ndarray:
        """同步提取特征（在线程池中执行）"""
        # 加载图像
        if isinstance(image_input, str):
            # 文件路径
            image = Image.open(image_input).convert('RGB')
        elif isinstance(image_input, bytes):
            # 字节数据
            image = Image.open(io.BytesIO(image_input)).convert('RGB')
        elif isinstance(image_input, Image.Image):
            # PIL Image对象
            image = image_input.convert('RGB')
        else:
            raise ValueError(f"不支持的图像输入类型: {type(image_input)}")
        
        # 预处理
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # 提取特征
        with torch.no_grad():
            features = self.model(input_tensor)
            features = features.squeeze().cpu().numpy()
            
            # 确保特征维度正确
            if features.shape[0] != self.feature_dim:
                self.logger.warning(
                    f"特征维度不匹配: 期望{self.feature_dim}, 实际{features.shape[0]}"
                )
            
            # L2 归一化
            features = features / np.linalg.norm(features)
            
        return features
    
    async def extract_batch_features(self, image_inputs: List[Union[str, Image.Image, bytes]]) -> np.ndarray:
        """
        批量提取图像特征
        
        Args:
            image_inputs: 图像输入列表
            
        Returns:
            特征矩阵，形状为 (N, feature_dim)
        """
        try:
            features_list = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._extract_batch_features_sync, image_inputs
            )
            return np.array(features_list)
        except Exception as e:
            self.logger.error(f"批量特征提取失败: {e}")
            raise
    
    def _extract_batch_features_sync(self, image_inputs: List[Union[str, Image.Image, bytes]]) -> List[np.ndarray]:
        """同步批量提取特征（在线程池中执行）"""
        features_list = []
        batch_size = settings.model.batch_size
        
        for i in range(0, len(image_inputs), batch_size):
            batch = image_inputs[i:i + batch_size]
            batch_tensors = []
            
            # 准备批次数据
            for image_input in batch:
                try:
                    # 加载和预处理图像
                    if isinstance(image_input, str):
                        image = Image.open(image_input).convert('RGB')
                    elif isinstance(image_input, bytes):
                        image = Image.open(io.BytesIO(image_input)).convert('RGB')
                    elif isinstance(image_input, Image.Image):
                        image = image_input.convert('RGB')
                    else:
                        continue
                    
                    tensor = self.transform(image)
                    batch_tensors.append(tensor)
                except Exception as e:
                    self.logger.warning(f"处理图像失败: {e}")
                    continue
            
            if not batch_tensors:
                continue
            
            # 批次推理
            batch_tensor = torch.stack(batch_tensors).to(self.device)
            with torch.no_grad():
                batch_features = self.model(batch_tensor)
                batch_features = batch_features.squeeze().cpu().numpy()
                
                # 处理单个样本的情况
                if len(batch_features.shape) == 1:
                    batch_features = batch_features.reshape(1, -1)
                
                # L2 归一化
                for j in range(batch_features.shape[0]):
                    feature = batch_features[j]
                    feature = feature / np.linalg.norm(feature)
                    features_list.append(feature)
        
        return features_list
    
    def get_feature_dim(self) -> int:
        """获取特征维度"""
        return self.feature_dim
    
    def is_initialized(self) -> bool:
        """检查模型是否已初始化"""
        return self.model is not None
    
    async def cleanup(self):
        """清理资源"""
        try:
            self.logger.info("正在清理模型服务资源...")
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
            
            # 清理GPU内存
            if self.device and self.device.type == 'cuda':
                torch.cuda.empty_cache()
            
            self.logger.info("模型服务资源清理完成")
        except Exception as e:
            self.logger.error(f"模型服务清理失败: {e}") 