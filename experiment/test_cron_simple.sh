#!/bin/bash
# 简单测试：模拟 crontab 环境运行 Python 脚本

echo "========================================="
echo "  模拟 Crontab 环境测试"
echo "========================================="
echo ""

# 设置 crontab 典型的最小环境变量
export PATH="/usr/bin:/bin"
export HOME="$HOME"
export USER="$USER"

echo "📋 模拟的 crontab 环境："
echo "   PATH: $PATH"
echo ""

# 检查命令
echo "🔍 检查命令可用性："
command -v node >/dev/null 2>&1 && echo "   ✅ node: $(which node)" || echo "   ❌ node: 未找到（预期）"
command -v claude >/dev/null 2>&1 && echo "   ✅ claude: $(which claude)" || echo "   ❌ claude: 未找到（预期）"
command -v python3 >/dev/null 2>&1 && echo "   ✅ python3: $(which python3)" || echo "   ❌ python3: 未找到"

echo ""
echo "========================================="
echo "  运行测试（使用 --no-claude 避免实际调用）"
echo "========================================="
echo ""

# 运行脚本，使用 --no-claude 避免实际调用 Claude
# 这样我们可以测试代码逻辑，而不会因为 Claude API 调用失败而中断
python3 worklog_summarizer.py 1 --no-claude

echo ""
echo "========================================="
echo "  如果上面没有错误，说明修复有效！"
echo "========================================="
