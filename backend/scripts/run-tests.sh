#!/bin/bash
# 运行后端测试脚本

set -e

echo "================================"
echo "运行后端测试"
echo "================================"

# 切换到backend目录
cd "$(dirname "$0")/.."

echo ""
echo "1. 检查Python环境..."
python3 --version

echo ""
echo "2. 运行单元测试..."
python3 -m pytest tests/unit/ -v --tb=short

echo ""
echo "3. 运行集成测试..."
python3 -m pytest tests/integration/ -v --tb=short

echo ""
echo "4. 生成测试覆盖率报告..."
python3 -m pytest tests/ --cov=. --cov-report=term-missing --cov-report=html

echo ""
echo "================================"
echo "测试完成！"
echo "================================"
echo ""
echo "查看详细覆盖率报告："
echo "  open htmlcov/index.html"
echo ""
