#!/usr/bin/env python3
"""
图与图寻 - 快速启动脚本
用于快速启动后端服务的便捷脚本
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="图与图寻快速启动脚本")
    parser.add_argument("--port", "-p", type=int, default=8000, help="服务端口号 (默认: 8000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="服务主机地址 (默认: 0.0.0.0)")
    parser.add_argument("--reload", action="store_true", help="启用热重载 (开发模式)")
    parser.add_argument("--workers", "-w", type=int, default=1, help="工作进程数 (默认: 1)")
    
    args = parser.parse_args()
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / "backend"
    
    print("🚀 正在启动图与图寻后端服务...")
    print(f"📂 项目目录: {project_root}")
    print(f"🌐 服务地址: http://{args.host}:{args.port}")
    print(f"📚 API文档: http://{args.host}:{args.port}/docs")
    print("-" * 50)
    
    # 检查是否在backend目录
    if not backend_dir.exists():
        print("❌ 找不到backend目录，请确保在正确的项目目录中运行此脚本")
        sys.exit(1)
    
    # 切换到backend目录
    os.chdir(backend_dir)
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        sys.exit(1)
    
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查依赖
    try:
        import uvicorn
        print("✅ Uvicorn已安装")
    except ImportError:
        print("❌ 缺少依赖，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # 创建必要的目录
    data_dirs = ["data/images", "data/index", "logs"]
    for dir_path in data_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {dir_path}")
    
    # 构建启动命令
    cmd = [
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", args.host,
        "--port", str(args.port)
    ]
    
    if args.reload:
        cmd.append("--reload")
        print("🔄 开发模式 - 启用热重载")
    
    if args.workers > 1:
        cmd.extend(["--workers", str(args.workers)])
        print(f"👥 使用 {args.workers} 个工作进程")
    
    print("🎯 启动命令:", " ".join(cmd))
    print("-" * 50)
    
    try:
        # 启动服务
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 