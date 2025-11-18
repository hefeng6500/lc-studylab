@echo off
REM LC-StudyLab Docker 一键启动脚本 (Windows)

echo ==========================================
echo LC-StudyLab Docker 部署脚本
echo ==========================================
echo.

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Docker，请先安装 Docker
    echo 安装指南: https://docs.docker.com/get-docker/
    exit /b 1
)

REM 检查 Docker Compose 是否安装
docker compose version >nul 2>&1
if errorlevel 1 (
    docker-compose --version >nul 2>&1
    if errorlevel 1 (
        echo [错误] 未检测到 Docker Compose，请先安装 Docker Compose
        echo 安装指南: https://docs.docker.com/compose/install/
        exit /b 1
    )
)

REM 检查 .env 文件是否存在
if not exist .env (
    echo [提示] 创建 .env 文件...
    if exist .env.example (
        copy .env.example .env >nul
        echo [成功] 已从 .env.example 创建 .env 文件
        echo.
        echo [警告] 请编辑 .env 文件，填写必要的配置（特别是 OPENAI_API_KEY）
        echo        编辑完成后，再次运行此脚本
        pause
        exit /b 0
    ) else (
        echo [错误] 未找到 .env.example 文件
        exit /b 1
    )
)

echo [提示] 开始构建和启动服务...
echo.

REM 构建并启动服务
docker compose up -d --build
if errorlevel 1 (
    docker-compose up -d --build
    if errorlevel 1 (
        echo [错误] 服务启动失败
        exit /b 1
    )
)

echo.
echo [提示] 等待服务启动...
timeout /t 5 /nobreak >nul

REM 检查服务状态
echo.
echo [状态] 服务状态:
docker compose ps 2>nul
if errorlevel 1 (
    docker-compose ps
)

echo.
echo ==========================================
echo [成功] 部署完成！
echo ==========================================
echo.
echo 访问地址:
echo   - 前端应用: http://localhost:3000
echo   - 后端 API: http://localhost:8000
echo   - API 文档: http://localhost:8000/docs
echo.
echo 常用命令:
echo   - 查看日志: docker-compose logs -f
echo   - 停止服务: docker-compose down
echo   - 重启服务: docker-compose restart
echo.
echo 详细文档请查看: DOCKER.md
echo.
pause

