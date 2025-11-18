#!/bin/bash
# 工作周报总结工具 - 便捷启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKLOG_SCRIPT="$SCRIPT_DIR/worklog_summarizer.py"

# 检查Python脚本是否存在
if [ ! -f "$WORKLOG_SCRIPT" ]; then
    echo -e "${YELLOW}错误：找不到 worklog_summarizer.py${NC}"
    echo "请确保脚本在相同目录下"
    exit 1
fi

# 显示欢迎信息
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}   工作周报总结工具${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# 询问天数
read -p "请输入要统计的天数 (默认7天): " DAYS
DAYS=${DAYS:-7}

# 验证输入
if ! [[ "$DAYS" =~ ^[0-9]+$ ]]; then
    echo -e "${YELLOW}警告：无效输入，使用默认7天${NC}"
    DAYS=7
fi

echo -e "${GREEN}正在生成过去 ${DAYS} 天的工作总结...${NC}"
echo ""

# 运行Python脚本
python3 "$WORKLOG_SCRIPT" "$DAYS"

# 检查是否成功
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ 总结完成！${NC}"
    # 查找最新的报告文件
    if [[ "$DAYS" == "5" ]]; then
        # 对于5天工作周，查找对应的文件
        LATEST_FILE=$(ls -t "$SCRIPT_DIR"/worklog_summary_*_to_*.txt 2>/dev/null | head -n 1)
    else
        # 对于其他天数
        LATEST_FILE=$(ls -t "$SCRIPT_DIR"/worklog_summary_*_to_*.txt 2>/dev/null | head -n 1)
    fi

    if [ -n "$LATEST_FILE" ]; then
        echo -e "报告文件：${BLUE}$LATEST_FILE${NC}"
        echo ""
        # 创建软链接 latest_weekly_journal 指向最新报告
        SYMLINK_PATH="$SCRIPT_DIR/latest_weekly_journal"
        # 删除旧的软链接（如果存在）
        if [ -L "$SYMLINK_PATH" ]; then
            rm "$SYMLINK_PATH"
        fi
        # 创建新的软链接
        ln -s "$LATEST_FILE" "$SYMLINK_PATH"
        echo -e "${GREEN}✅ 已创建软链接：${BLUE}$SYMLINK_PATH${NC}"
        echo -e "   发送端可直接读取：${YELLOW}$SYMLINK_PATH${NC}"
        echo ""
        echo -e "${YELLOW}是否要打开报告文件？(y/N)${NC}"
        read -r OPEN_FILE
        if [[ "$OPEN_FILE" =~ ^[Yy]$ ]]; then
            if command -v less &> /dev/null; then
                less "$LATEST_FILE"
            elif command -v cat &> /dev/null; then
                cat "$LATEST_FILE"
            else
                echo "无法打开文件，请手动查看"
            fi
        fi
    else
        echo "未找到生成的报告文件"
    fi
else
    echo -e "${YELLOW}❌ 生成报告时出现错误${NC}"
    exit 1
fi