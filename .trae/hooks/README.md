# Git Hooks 配置说明

## 📋 概述

本项目配置了 Git 提交前检查脚本，在每次提交前自动：
1. 生成提交摘要（文件分类、变更统计）
2. 检查代码质量（调试代码、敏感信息、TODO/FIXME）
3. 要求用户审查后再提交

## 🔧 安装步骤

### 1. 赋予脚本执行权限
```bash
chmod +x .trae/hooks/pre-commit-check.py
```

### 2. 配置 Git Hook
在项目根目录执行以下命令之一：

#### 方式一：使用 Git Hook 目录
```bash
# 创建 .git/hooks 目录（如果不存在）
mkdir -p .git/hooks

# 创建符号链接
ln -sf ../../.trae/hooks/pre-commit-check.py .git/hooks/pre-commit
```

#### 方式二：使用 Husky（推荐）
如果项目使用 Husky：
```bash
# 安装 Husky（如果未安装）
npm install husky --save-dev

# 配置 pre-commit hook
npx husky add .husky/pre-commit ".trae/hooks/pre-commit-check.py"
```

#### 方式三：使用 pre-commit 框架
如果项目使用 pre-commit 框架，在 `.pre-commit-config.yaml` 中添加：
```yaml
repos:
  - repo: local
    hooks:
      - id: project-pre-commit-check
        name: Project Pre-commit Check
        entry: .trae/hooks/pre-commit-check.py
        language: system
        pass_filenames: false
        always_run: true
```

## 📊 功能说明

### 1. 提交摘要
自动分类和统计暂存的文件：
- **Python**: `.py` 文件
- **JavaScript/TypeScript**: `.js`, `.ts`, `.jsx`, `.tsx` 文件
- **文档**: `.md` 文件
- **配置**: `.json`, `.yaml`, `.yml`, `.toml` 文件
- **数据库**: `.sql` 文件
- **脚本**: `.sh`, `.bash` 文件
- **其他**: 其他文件类型

输出内容包括：
- 各类别的文件数量
- 代码变更统计（+新增 -删除）
- 文件列表

### 2. 代码质量检查
自动检查 Python 文件中的：
- **TODO/FIXME**: 标记未完成的工作
- **调试代码**: `debug=True`, `pdb` 等
- **敏感信息**: `password`, `secret` 等关键字

### 3. 审查提示
在提交前要求用户确认：
1. 检查文件分类是否正确
2. 检查代码变更是否符合预期
3. 检查是否有敏感信息泄露
4. 检查是否有调试代码残留
5. 检查提交信息是否准确描述变更

## 🚀 使用示例

### 正常提交流程
```bash
# 1. 暂存文件
git add .

# 2. 提交（自动触发检查）
git commit -m "feat: 添加用户认证功能"
```

### 输出示例
```
============================================================
📋 Git 提交摘要
============================================================

📁 文件分类统计：

  Python:
    文件数: 3
    变更: +150 -20
    文件列表:
      - backend/api/auth.py
      - backend/services/auth_service.py
      - backend/models/user.py

  配置:
    文件数: 1
    变更: +5 -0
    文件列表:
      - backend/config/settings.py

============================================================
📊 总体统计：
  文件总数: 4
  代码变更: +155 -20
============================================================

🔍 代码质量检查：

✅ 未发现明显问题

============================================================
⚠️  请审查以上内容：
============================================================

确认事项：
  1. 检查文件分类是否正确
  2. 检查代码变更是否符合预期
  3. 检查是否有敏感信息泄露
  4. 检查是否有调试代码残留
  5. 检查提交信息是否准确描述变更

是否继续提交？(y/n): y

✅ 继续提交...
```

### 取消提交
```bash
# 在审查提示时输入 n 或 no
是否继续提交？(y/n): n

❌ 提交已取消
```

## 🔍 自定义配置

### 修改文件分类规则
编辑 `.trae/hooks/pre-commit-check.py` 中的 `categorize_file` 函数：

```python
def categorize_file(file_path):
    """对文件进行分类"""
    ext = Path(file_path).suffix.lower()
    
    # 添加自定义分类
    if ext in ['.go']:
        return 'Go'
    elif ext in ['.java']:
        return 'Java'
    # ...
```

### 修改代码检查规则
编辑 `.trae/hooks/pre-commit-check.py` 中的 `check_code_quality` 函数：

```python
# 添加自定义检查
if 'print(' in line:
    issues.append(f"  {file_path}:{i} - 警告：调试打印语句")
```

### 跳过检查
如果需要临时跳过检查：
```bash
git commit --no-verify -m "紧急修复"
```

## 📝 注意事项

1. **首次安装**: 需要手动配置 Git Hook
2. **权限问题**: 确保脚本有执行权限
3. **Python 环境**: 脚本需要 Python 3.6+
4. **Git 版本**: 需要 Git 2.0+

## 🔗 相关文档

- [Git Hooks 文档](https://git-scm.com/book/en/v2/Git-Customizing-Git-Git-Hooks)
- [Pre-commit 框架](https://pre-commit.com/)
- [Husky](https://typicode.github.io/husky/)

## 📅 更新历史

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026-03-19 | 1.0 | 初始版本，实现基础检查功能 |
