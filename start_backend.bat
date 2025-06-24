@echo off
REM 图与图寻后端启动脚本
REM 解决OpenMP库冲突问题

echo 🚀 启动图与图寻后端服务...

REM 设置环境变量解决OpenMP冲突
set KMP_DUPLICATE_LIB_OK=TRUE
set OMP_NUM_THREADS=1

REM 切换到后端目录
cd /d %~dp0backend

REM 检查虚拟环境
if exist venv (
    echo 📦 激活虚拟环境...
    call venv\Scripts\activate
)

REM 启动服务
echo 🌟 启动FastAPI服务器...
python main.py

pause 