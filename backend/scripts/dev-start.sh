#!/bin/bash

# 前后端联调启动脚本

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}🚀 启动前后端联调环境...${NC}"

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker未运行，请先启动Docker${NC}"
    exit 1
fi

# 检查.env文件
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  .env文件不存在，从.env.example创建...${NC}"
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo -e "${GREEN}✅ 已创建.env文件，请根据需要修改配置${NC}"
fi

# 停止旧容器
echo -e "${YELLOW}🛑 停止旧容器...${NC}"
cd "$PROJECT_DIR"
docker-compose -f docker-compose.dev.yml down

# 启动开发环境
echo -e "${YELLOW}🔧 启动开发环境...${NC}"
docker-compose -f docker-compose.dev.yml up -d

# 等待服务启动
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 8

# 检查服务状态
echo -e "${GREEN}📊 检查服务状态...${NC}"
docker-compose -f docker-compose.dev.yml ps

# 健康检查
echo -e "${YELLOW}🔍 健康检查...${NC}"
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:5001/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端服务健康检查通过${NC}"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -e "${YELLOW}⏳ 等待后端服务启动... ($RETRY_COUNT/$MAX_RETRIES)${NC}"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ 后端服务启动失败${NC}"
    echo -e "${YELLOW}查看日志：docker-compose -f docker-compose.dev.yml logs backend${NC}"
    exit 1
fi

# 显示服务地址
echo ""
echo -e "${GREEN}✅ 前后端联调环境启动完成！${NC}"
echo ""
echo -e "${GREEN}📡 服务地址：${NC}"
echo -e "   - 后端API: ${GREEN}http://localhost:5001${NC}"
echo -e "   - WebSocket: ${GREEN}ws://localhost:5001/ws${NC}"
echo -e "   - MySQL: ${GREEN}localhost:3306${NC}"
echo -e "   - Redis: ${GREEN}localhost:6379${NC}"
echo ""
echo -e "${GREEN}📁 项目结构：${NC}"
echo -e "   - 后端: ${GREEN}./backend${NC} (完全独立)"
echo -e "   - 前端: ${GREEN}../frontend${NC}"
echo -e "   - 文档: ${GREEN}./backend/docs${NC}"
echo -e "   - 脚本: ${GREEN}./backend/scripts${NC}"
echo ""
echo -e "${GREEN}📱 前端项目：${NC}"
echo -e "   - 在微信开发者工具中打开: ${GREEN}$(dirname "$PROJECT_DIR")/frontend${NC}"
echo ""
echo -e "${GREEN}🔧 开发工具：${NC}"
echo -e "   - 查看后端日志: ${GREEN}docker-compose -f docker-compose.dev.yml logs -f backend${NC}"
echo -e "   - 重启后端服务: ${GREEN}docker-compose -f docker-compose.dev.yml restart backend${NC}"
echo -e "   - 进入后端容器: ${GREEN}docker exec -it undercover-backend-dev bash${NC}"
echo ""
echo -e "${GREEN}🧪 测试工具：${NC}"
echo -e "   - 运行后端测试: ${GREEN}cd backend && python3 -m pytest${NC}"
echo -e "   - 运行前端测试: ${GREEN}cd ../frontend && npm test${NC}"
echo -e "   - API健康检查: ${GREEN}curl http://localhost:5001/health${NC}"
echo ""
echo -e "${GREEN}🛑 停止服务：${NC}"
echo -e "   ${GREEN}./scripts/dev-stop.sh${NC}"
echo ""
