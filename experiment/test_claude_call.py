#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证在 crontab 环境中能否正确找到 node 和调用 claude
"""

import os
import sys
import subprocess

# 模拟 crontab 环境
os.environ['PATH'] = '/usr/bin:/bin'

print("=" * 80)
print("  测试 Crontab 环境下的 Claude 调用")
print("=" * 80)
print()

print("📋 当前环境：")
print(f"   PATH: {os.environ.get('PATH', '')}")
print()

# 导入配置
try:
    sys.path.insert(0, os.path.dirname(__file__))
    from config import CLAUDE_PATH
    print(f"✅ 配置文件加载成功")
    print(f"   CLAUDE_PATH: {CLAUDE_PATH}")
    print()
except Exception as e:
    print(f"❌ 加载配置失败: {e}")
    sys.exit(1)

# 测试 node 查找逻辑
print("🔍 测试 node 查找逻辑：")
import shutil
node_path = None
claude_dir = os.path.dirname(CLAUDE_PATH)

# 优先尝试从 claude 的目录推断 node 路径
potential_node = os.path.join(claude_dir, 'node')
if os.path.exists(potential_node) and os.access(potential_node, os.X_OK):
    node_path = potential_node
    print(f"   ✅ 从 claude 目录找到 node: {node_path}")
else:
    print(f"   ❌ claude 目录下没有 node: {potential_node}")
    node_path = shutil.which('node')
    if node_path:
        print(f"   ✅ 通过 which 找到 node: {node_path}")
    else:
        print(f"   ❌ 无法找到 node")

print()

# 测试 claude 脚本路径
print("🔍 测试 claude 脚本路径：")
claude_actual = os.path.realpath(CLAUDE_PATH)
print(f"   CLAUDE_PATH: {CLAUDE_PATH}")
print(f"   实际路径: {claude_actual}")
if claude_actual.endswith('.js'):
    print(f"   ✅ 是 JavaScript 文件")
    claude_script = claude_actual
else:
    print(f"   ⚠️  不是 .js 文件，使用原始路径")
    claude_script = CLAUDE_PATH

print()

# 测试环境变量设置
print("🔍 测试环境变量设置：")
env = os.environ.copy()
if node_path:
    node_dir = os.path.dirname(node_path)
    current_path = env.get('PATH', '')
    if node_dir not in current_path.split(os.pathsep):
        env['PATH'] = f"{node_dir}{os.pathsep}{current_path}"
        print(f"   ✅ 已添加 node 路径到 PATH: {node_dir}")
        print(f"   新 PATH: {env['PATH']}")
    else:
        print(f"   ⚠️  node 路径已在 PATH 中")
else:
    print(f"   ❌ 无法设置 PATH（找不到 node）")

print()

# 测试命令构建
print("🔍 测试命令构建：")
if node_path:
    cmd = [node_path, claude_script, '--version']
    print(f"   命令: {' '.join(cmd)}")
    print()
    
    # 尝试执行命令（只测试能否找到 node，不实际调用 API）
    print("🚀 测试执行命令（获取版本信息）：")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
            env=env
        )
        
        if result.returncode == 0:
            print(f"   ✅ 命令执行成功！")
            print(f"   输出: {result.stdout.strip()}")
        else:
            print(f"   ⚠️  命令执行失败（返回码: {result.returncode}）")
            print(f"   错误: {result.stderr.strip()}")
            if "node" in result.stderr.lower() or "找不到" in result.stderr:
                print(f"   ❌ 这表示仍然无法找到 node，修复可能无效")
            else:
                print(f"   ℹ️  这可能是其他错误（如 API 密钥问题），不是 node 路径问题")
    except subprocess.TimeoutExpired:
        print(f"   ⏰ 命令超时")
    except Exception as e:
        print(f"   ❌ 执行出错: {e}")
else:
    print(f"   ❌ 无法构建命令（找不到 node）")

print()
print("=" * 80)
print("  测试完成")
print("=" * 80)
print()
print("💡 如果看到 '✅ 命令执行成功'，说明修复有效！")
print("   如果看到 node 相关的错误，说明还需要进一步修复")
