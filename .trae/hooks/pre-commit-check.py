#!/usr/bin/env python3
"""
Git 提交前检查脚本
功能：生成提交摘要并要求用户审查
"""

import subprocess
import sys
import os
from pathlib import Path

def get_staged_files():
    """获取暂存的文件列表"""
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only'],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip().split('\n') if result.stdout.strip() else []

def get_file_stats(file_path):
    """获取文件统计信息"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--numstat', '--', file_path],
            capture_output=True,
            text=True,
            check=True
        )
        lines = result.stdout.strip().split('\n')
        if lines and lines[0]:
            parts = lines[0].split('\t')
            added = int(parts[0]) if parts[0].isdigit() else 0
            deleted = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
            return added, deleted
        return 0, 0
    except:
        return 0, 0

def categorize_file(file_path):
    """对文件进行分类"""
    ext = Path(file_path).suffix.lower()
    
    if ext in ['.py']:
        return 'Python'
    elif ext in ['.js', '.ts', '.jsx', '.tsx']:
        return 'JavaScript/TypeScript'
    elif ext in ['.md']:
        return '文档'
    elif ext in ['.json', '.yaml', '.yml', '.toml']:
        return '配置'
    elif ext in ['.sql']:
        return '数据库'
    elif ext in ['.sh', '.bash']:
        return '脚本'
    else:
        return '其他'

def generate_summary():
    """生成提交摘要"""
    staged_files = get_staged_files()
    
    if not staged_files:
        print("⚠️  没有暂存的文件，无法生成摘要")
        return False
    
    print("\n" + "="*60)
    print("📋 Git 提交摘要")
    print("="*60 + "\n")
    
    # 按类别统计
    categories = {}
    total_added = 0
    total_deleted = 0
    
    for file_path in staged_files:
        category = categorize_file(file_path)
        added, deleted = get_file_stats(file_path)
        
        if category not in categories:
            categories[category] = {'files': [], 'added': 0, 'deleted': 0}
        
        categories[category]['files'].append(file_path)
        categories[category]['added'] += added
        categories[category]['deleted'] += deleted
        
        total_added += added
        total_deleted += deleted
    
    # 输出分类摘要
    print("📁 文件分类统计：\n")
    for category, data in categories.items():
        file_count = len(data['files'])
        added = data['added']
        deleted = data['deleted']
        
        print(f"  {category}:")
        print(f"    文件数: {file_count}")
        if added > 0 or deleted > 0:
            print(f"    变更: +{added} -{deleted}")
        print(f"    文件列表:")
        for file_path in data['files']:
            print(f"      - {file_path}")
        print()
    
    # 输出总体统计
    print("="*60)
    print(f"📊 总体统计：")
    print(f"  文件总数: {len(staged_files)}")
    print(f"  代码变更: +{total_added} -{total_deleted}")
    print("="*60 + "\n")
    
    return True

def check_code_quality():
    """检查代码质量（基础检查）"""
    staged_files = get_staged_files()
    python_files = [f for f in staged_files if f.endswith('.py')]
    
    if not python_files:
        return True
    
    print("🔍 代码质量检查：\n")
    
    issues = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # 检查 TODO/FIXME
            for i, line in enumerate(lines, 1):
                if 'TODO' in line or 'FIXME' in line:
                    issues.append(f"  {file_path}:{i} - 发现 TODO/FIXME")
                
                # 检查调试代码
                if 'debug=True' in line or 'pdb' in line:
                    issues.append(f"  {file_path}:{i} - 警告：调试代码")
                
                # 检查敏感信息
                if 'password' in line.lower() or 'secret' in line.lower():
                    if '=' in line and '"' in line:
                        issues.append(f"  {file_path}:{i} - 警告：可能包含敏感信息")
        
        except Exception as e:
            issues.append(f"  {file_path} - 无法读取文件: {e}")
    
    if issues:
        print("发现以下问题：\n")
        for issue in issues:
            print(issue)
        print()
    else:
        print("✅ 未发现明显问题\n")
    
    return True

def prompt_review():
    """提示用户审查"""
    print("="*60)
    print("⚠️  请审查以上内容：")
    print("="*60)
    print()
    print("确认事项：")
    print("  1. 检查文件分类是否正确")
    print("  2. 检查代码变更是否符合预期")
    print("  3. 检查是否有敏感信息泄露")
    print("  4. 检查是否有调试代码残留")
    print("  5. 检查提交信息是否准确描述变更")
    print()
    
    response = input("是否继续提交？(y/n): ").strip().lower()
    
    if response not in ['y', 'yes']:
        print("\n❌ 提交已取消")
        sys.exit(1)
    
    print("\n✅ 继续提交...\n")

def main():
    """主函数"""
    try:
        # 生成摘要
        if not generate_summary():
            sys.exit(1)
        
        # 检查代码质量
        check_code_quality()
        
        # 提示审查
        prompt_review()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 命令执行失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n❌ 操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
