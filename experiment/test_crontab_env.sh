#!/bin/bash
# 模拟 crontab 环境来测试脚本
# crontab 通常只有最小的 PATH: /usr/bin:/bin

set -e

echo "========================================="
echo "  模拟 Crontab 环境测试"
echo "========================================="
echo ""

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKLOG_SCRIPT="$SCRIPT_DIR/worklog_summarizer.py"

# 显示当前环境
echo "📋 当前环境变量："
echo "   PATH: $PATH"
echo "   HOME: $HOME"
echo "   USER: $USER"
echo ""

# 模拟 crontab 的最小环境
echo "🔧 模拟 crontab 环境（最小 PATH）..."
echo ""

# 设置 crontab 典型的最小环境变量
# 注意：crontab 通常只有 /usr/bin:/bin 在 PATH 中
export PATH="/usr/bin:/bin"
export HOME="$HOME"
export USER="$USER"
export SHELL="/bin/bash"

echo "📋 Crontab 模拟环境："
echo "   PATH: $PATH"
echo "   HOME: $HOME"
echo "   USER: $USER"
echo ""

# 检查是否能找到 node 和 claude（应该找不到）
echo "🔍 检查命令可用性："
if command -v node >/dev/null 2>&1; then
    echo "   ✅ node: $(which node)"
else
    echo "   ❌ node: 未找到（这是预期的）"
fi

if command -v claude >/dev/null 2>&1; then
    echo "   ✅ claude: $(which claude)"
else
    echo "   ❌ claude: 未找到（这是预期的）"
fi

if command -v python3 >/dev/null 2>&1; then
    echo "   ✅ python3: $(which python3)"
else
    echo "   ❌ python3: 未找到"
    exit 1
fi

echo ""
echo "========================================="
echo "  运行工作日志总结脚本（测试修复）"
echo "========================================="
echo ""

# 运行脚本（使用 --no-claude 避免实际调用 Claude，只测试是否能找到 node）
# 或者使用一个很小的天数来快速测试
python3 "$WORKLOG_SCRIPT" 1 --no-claude

echo ""
echo "========================================="
echo "  测试完成"
echo "========================================="
echo ""
echo "💡 如果上面的测试成功，说明修复有效"
echo "   如果仍然失败，可能需要进一步调整代码"
