#!/bin/bash

# 前后端联调停止脚本

set -e

# 项目路径
BACKEND_DIR="/Users/xlxing/PycharmProjects/mp-undercover"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 停止前后端联调环境...${NC}"

# 停止并删除容器
cd "$BACKEND_DIR"
docker-compose -f docker-compose.dev.yml down

echo -e "${GREEN}✅ 前后端联调环境已停止${NC}"
echo ""
echo -e "${GREEN}💡 如需重新启动，请运行：${NC}"
echo -e "   ${GREEN}./scripts/dev-start.sh${NC}"
echo ""
