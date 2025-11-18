#!/bin/bash
# 工作周报定时生成和推送脚本 - 适用于crontab
# 该脚本会自动生成过去7天的工作总结并推送到RocketChat

set -e

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKLOG_SCRIPT="$SCRIPT_DIR/worklog_summarizer.py"
PUSH_SCRIPT="/home/spin6lock/opensource/push_to_rocketchat/push_worklog.py"
DAYS=7

echo "========================================="
echo "  定时工作周报生成和推送"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="

# 1. 生成工作周报
echo "正在生成过去 ${DAYS} 天的工作总结..."

# 直接调用Python脚本，传递天数参数（避免交互式输入）
python3 "$WORKLOG_SCRIPT" "$DAYS"

if [ $? -ne 0 ]; then
    echo "❌ 生成工作周报失败"
    exit 1
fi

echo "✅ 工作周报生成完成"

# 2. 查找最新的报告文件
echo "查找最新生成的报告文件..."
LATEST_FILE=$(ls -t "$SCRIPT_DIR"/latest_weekly_journal 2>/dev/null | head -n 1)

if [ -z "$LATEST_FILE" ]; then
    echo "❌ 未找到生成的报告文件"
    exit 1
fi

echo "📄 报告文件：$LATEST_FILE"

# 3. 推送到RocketChat
echo "正在推送到RocketChat频道 #week_journal..."

# 调用推送脚本，使用找到的最新文件
python3 "$PUSH_SCRIPT" "$LATEST_FILE" "#week_journal"

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "  ✅ 全部完成！"
    echo "  $(date '+%Y-%m-%d %H:%M:%S')"
    echo "========================================="
    exit 0
else
    echo "❌ 推送到RocketChat失败"
    exit 1
fi
