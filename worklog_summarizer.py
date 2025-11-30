#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作日志收集器
收集指定目录下的工作日志文件，为Claude分析准备输入
支持多种日期格式：YYYYMMDD.md, YYYYMMDD星期五.md等
"""

import os
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


class WorklogCollector:
    def __init__(self, base_path: str):
        """
        初始化工作日志收集器

        Args:
            base_path: 工作日志根目录路径
        """
        self.base_path = Path(base_path)
        self.current_year = datetime.now().year
        self.log_files = []

    def parse_date_from_filename(self, filename: str) -> Optional[datetime]:
        """
        从文件名中解析日期

        支持格式：
        - YYYYMMDD.md (如: 20251107.md)
        - YYYYMMDD星期五.md (如: 20251107星期五.md)
        - YYYYMMDD周X.md (如: 20251107周5.md)
        - YYYYMMDD_其他文字.md

        Args:
            filename: 文件名

        Returns:
            解析后的日期对象，解析失败返回None
        """
        # 移除.md扩展名
        name = filename.replace('.md', '')

        # 匹配日期部分：YYYYMMDD
        date_pattern = r'(\d{4})(\d{2})(\d{2})'
        match = re.search(date_pattern, name)

        if match:
            year, month, day = map(int, match.groups())
            try:
                return datetime(year, month, day)
            except ValueError:
                return None

        return None

    def find_recent_logs(self, days: int = 7) -> List[Path]:
        """
        查找过去N天的工作日志文件

        Args:
            days: 天数，默认为7天

        Returns:
            工作日志文件路径列表
        """
        # 如果是5天工作日，使用工作周逻辑
        if days == 5:
            return self.find_recent_work_week_logs()

        # 其他天数使用原逻辑
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        log_files = []

        # 遍历年份目录
        for year_dir in self.base_path.iterdir():
            if not year_dir.is_dir() or year_dir.name != str(self.current_year):
                continue

            # 遍历月份目录
            for month_dir in year_dir.iterdir():
                if not month_dir.is_dir():
                    continue

                # 跳过隐藏目录
                if month_dir.name.startswith('.'):
                    continue

                try:
                    month_num = int(month_dir.name)
                    if month_num < 1 or month_num > 12:
                        continue
                except ValueError:
                    continue

                # 遍历日志文件
                for log_file in month_dir.glob("*.md"):
                    # 解析文件名中的日期
                    file_date = self.parse_date_from_filename(log_file.name)
                    # 只比较日期部分，不比较时间部分
                    if file_date and file_date.date() >= start_date.date() and file_date.date() <= end_date.date():
                        log_files.append(log_file)

        return sorted(log_files)

    def find_recent_work_week_logs(self) -> List[Path]:
        """
        查找最近的完整工作周（周一到周五）日志文件

        Returns:
            工作日志文件路径列表
        """
        today = datetime.now()
        # 计算今天是周几 (0=周一, 6=周日)
        today_weekday = today.weekday()

        # 如果今天是周一到周四，取上周一到上周五
        if today_weekday in [0, 1, 2, 3]:
            # 上周的周一
            days_since_monday = today_weekday
            last_monday = today - timedelta(days=days_since_monday + 7)
        else:  # 周五、周六、周日 (4, 5, 6)
            # 本周的周一
            days_since_monday = today_weekday
            last_monday = today - timedelta(days=days_since_monday)

        # 工作周是周一到周五
        start_date = last_monday
        end_date = last_monday + timedelta(days=4)  # 周五

        log_files = []

        # 遍历年份目录
        for year_dir in self.base_path.iterdir():
            if not year_dir.is_dir() or year_dir.name != str(self.current_year):
                continue

            # 遍历月份目录
            for month_dir in year_dir.iterdir():
                if not month_dir.is_dir():
                    continue

                # 跳过隐藏目录
                if month_dir.name.startswith('.'):
                    continue

                try:
                    month_num = int(month_dir.name)
                    if month_num < 1 or month_num > 12:
                        continue
                except ValueError:
                    continue

                # 遍历日志文件
                for log_file in month_dir.glob("*.md"):
                    # 解析文件名中的日期
                    file_date = self.parse_date_from_filename(log_file.name)
                    # 只比较日期部分，不比较时间部分
                    if file_date and file_date.date() >= start_date.date() and file_date.date() <= end_date.date():
                        log_files.append(log_file)

        return sorted(log_files)

    def parse_log_file(self, file_path: Path) -> Dict:
        """
        解析单个工作日志文件

        Args:
            file_path: 日志文件路径

        Returns:
            解析后的日志内容字典
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取日期
        file_date = self.parse_date_from_filename(file_path.name)
        if file_date:
            date_str = file_date.strftime('%Y-%m-%d')
        else:
            date_str = "未知日期"

        # 提取任务
        tasks = {
            'completed': [],  # 已完成任务
            'pending': []     # 未完成任务
        }

        # 匹配任务项 [-] 或 [x]
        task_pattern = r'^\s*-\s*\[([x ])\]\s*(.+)$'
        for line in content.split('\n'):
            match = re.match(task_pattern, line, re.MULTILINE)
            if match:
                status, task = match.groups()
                task = task.strip()
                if status.lower() == 'x':
                    tasks['completed'].append(task)
                else:
                    tasks['pending'].append(task)

        # 提取引用内容（以> 开头或## 开头的部分）
        sections = []
        current_section = None
        current_content = []

        for line in content.split('\n'):
            if line.startswith('##'):
                if current_section:
                    sections.append({
                        'title': current_section,
                        'content': '\n'.join(current_content).strip()
                    })
                current_section = line.lstrip('#').strip()
                current_content = []
            else:
                current_content.append(line)

        # 添加最后一个section
        if current_section:
            sections.append({
                'title': current_section,
                'content': '\n'.join(current_content).strip()
            })

        return {
            'date': date_str,
            'file_path': str(file_path),
            'tasks': tasks,
            'sections': sections,
            'raw_content': content
        }

    def collect_logs_for_claude(self, days: int = 7) -> str:
        """
        收集并整理日志内容，为Claude分析准备输入

        Args:
            days: 天数

        Returns:
            格式化的日志内容，可直接发送给Claude
        """
        # 计算工作周日期范围
        if days == 5:
            today = datetime.now()
            today_weekday = today.weekday()

            if today_weekday in [0, 1, 2, 3]:  # 周一到周四
                days_since_monday = today_weekday
                last_monday = today - timedelta(days=days_since_monday + 7)
            else:  # 周五到周日
                days_since_monday = today_weekday
                last_monday = today - timedelta(days=days_since_monday)

            week_end = last_monday + timedelta(days=4)  # 周五
            week_range = f"{last_monday.strftime('%Y-%m-%d')} 至 {week_end.strftime('%Y-%m-%d')}"
            print(f"🔍 正在收集工作周日志：{week_range}")
            stats_range = f"工作周：{week_range}"
        else:
            print(f"🔍 正在收集过去 {days} 天的工作日志...")
            stats_range = f"过去 {days} 天"

        log_files = self.find_recent_logs(days)

        if not log_files:
            print("❌ 未找到工作日志文件")
            return "未找到工作日志文件"

        print(f"✅ 找到 {len(log_files)} 个工作日志文件")

        logs = []
        for log_file in log_files:
            try:
                log_data = self.parse_log_file(log_file)
                logs.append(log_data)
            except Exception as e:
                print(f"  ⚠️  解析文件失败 {log_file}: {e}")

        # 生成Claude输入格式
        claude_input = []
        claude_input.append("=" * 80)
        claude_input.append("工作日志内容汇总")
        claude_input.append("=" * 80)
        claude_input.append(f"统计时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        claude_input.append(f"统计范围：{stats_range}")
        claude_input.append(f"日志天数：{len(logs)} 天")
        claude_input.append("")

        for log in logs:
            claude_input.append("=" * 80)
            claude_input.append(f"日期：{log['date']}")
            claude_input.append(f"文件：{log['file_path']}")
            claude_input.append("=" * 80)
            claude_input.append("")
            claude_input.append(log['raw_content'])
            claude_input.append("")
            claude_input.append("")
            claude_input.append("-" * 80)
            claude_input.append("")

        return '\n'.join(claude_input)

    def save_claude_input(self, days: int = 7, output_file: str = "claude_input.txt"):
        """
        保存收集的日志内容到文件

        Args:
            days: 天数
            output_file: 输出文件名
        """
        content = self.collect_logs_for_claude(days)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"📄 原始日志内容已保存到：{output_file}")
        print(f"   可以将文件内容复制给Claude进行分析")
        return output_file

    def call_claude_analysis(self, log_content: str, prompt_file: str = None) -> str:
        """
        调用Claude分析工作日志

        Args:
            log_content: 工作日志内容
            prompt_file: 可选的分析提示词文件路径

        Returns:
            Claude的分析结果
        """
        print("🤖 正在调用Claude进行智能分析...")

        # 读取分析提示词
        if prompt_file and os.path.exists(prompt_file):
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    analysis_prompt = f.read()
            except Exception as e:
                print(f"  ⚠️  读取提示词文件失败: {e}")
                analysis_prompt = None
        else:
            # 使用默认提示词
            analysis_prompt = self._get_default_analysis_prompt()

        # 构建完整的提示词
        full_prompt = f"""
{analysis_prompt}

{'=' * 80}
工作日志内容：
{'=' * 80}

{log_content}

请开始分析。
"""

        try:
            # 读取配置文件获取 CLAUDE_PATH
            from config import CLAUDE_PATH

            # 调用Claude CLI
            result = subprocess.run(
                [CLAUDE_PATH, '-p', '--output-format', 'text', full_prompt],
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )

            if result.returncode == 0:
                print("✅ Claude分析完成！")
                return result.stdout
            else:
                print(f"❌ Claude调用失败: {result.stderr}")
                return f"Claude调用失败: {result.stderr}"

        except subprocess.TimeoutExpired:
            print("⏰ Claude分析超时（5分钟）")
            return "分析超时，请重试或手动分析"
        except Exception as e:
            print(f"❌ 调用Claude时发生错误: {e}")
            return f"调用错误: {e}"

    def _get_default_analysis_prompt(self) -> str:
        """
        获取默认的Claude分析提示词

        Returns:
            分析提示词
        """
        return """# Claude工作日志分析指令

请分析以下工作日志内容，并提供详细的工作总结和建议。

## 分析要求

请从以下几个方面对工作日志进行深度分析：

### 1. 📊 整体统计与分析
- 统计过去5天的日志天数（代表上个完整5天工作日）
- 计算总任务数、已完成任务数、未完成任务数
- 计算任务完成率
- 分析工作节奏和效率

### 2. 🏷️ 工作分类与主题
根据日志内容，将工作按主题分类：
- 技术开发类
- 配置与资产管理
- 测试与联调
- 文档与规划
- 其他类别
- 统计每个分类的工作量

### 4. 🎯 关键成果与亮点
- 列出最重要的已完成工作
- 标注技术突破或重要进展
- 总结可量化的成果

### 5. ⚠️ 问题与风险
- 识别未完成的关键任务
- 分析可能的阻塞点
- 提出风险预警

### 6. 💡 改进建议
- 工作方法优化建议
- 任务管理改进建议
- 时间分配优化建议
- 流程改进建议

### 7. 📋 下周工作计划建议
基于未完成任务和项目进展，建议下周重点工作：
- 优先级排序
- 时间预估
- 依赖关系

## 输出格式要求

请使用以下格式组织分析结果：

```markdown
# 工作周报总结分析

## 📈 整体统计
- 统计周期：过去5天工作日（上个完整工作周）
- 日志天数：X天
- 总任务数：X项
- 已完成：X项
- 待完成：X项
- 完成率：X%

## 📊 工作分类统计
- 分类1：X次
- 分类2：X次
- ...

## ⭐ 关键成果与亮点
1. 成果1
   - 具体描述
2. 成果2
   - 具体描述

## ⚠️ 问题与风险
### 未完成任务
1. 任务1（优先级：高/中/低）
   - 原因分析
2. 任务2

### 风险提示
- 风险1
- 风险2

## 💡 改进建议
### 工作方法
- 建议1
- 建议2

### 任务管理
- 建议1
- 建议2

### 流程优化
- 建议1
- 建议2

## 📅 下周工作建议
### 高优先级
1. 任务1
   - 预估时间
   - 关键依赖

### 中优先级
1. 任务1
   - 预估时间
   - 关键依赖

### 低优先级
1. 任务1
   - 预估时间
   - 关键依赖
```

## 注意事项

1. **统计周期**：默认统计过去5天工作日（完整工作周）
2. **客观公正**：基于实际日志内容进行分析，避免主观臆断
3. **数据驱动**：用具体数字和事实支撑分析结论
4. **可执行性**：建议要具体可操作
5. **优先级明确**：帮助区分任务的轻重缓急
6. **价值导向**：关注对项目/业务有实际价值的成果
7. **精简分析**：无需详细列出每日工作内容，重点关注统计和分类
"""

    def generate_output_filename(self, days: int = 5, claude_input_dir: str = "claude_input",
                                  worklog_summary_dir: str = "worklog_summary") -> tuple:
        """
        根据天数和日期范围生成输出文件名

        Args:
            days: 统计天数
            claude_input_dir: Claude输入文件目录
            worklog_summary_dir: 工作总结报告目录

        Returns:
            tuple: (输出文件名, 输入文件名)
        """
        if days == 5:
            # 计算工作周范围
            today = datetime.now()
            today_weekday = today.weekday()

            if today_weekday in [0, 1, 2, 3]:  # 周一到周四
                days_since_monday = today_weekday
                last_monday = today - timedelta(days=days_since_monday + 7)
            else:  # 周五到周日
                days_since_monday = today_weekday
                last_monday = today - timedelta(days=days_since_monday)

            week_end = last_monday + timedelta(days=4)  # 周五

            # 生成文件名：worklog_summary_YYYYMMDD_to_YYYYMMDD.txt
            output_file = f"{worklog_summary_dir}/worklog_summary_{last_monday.strftime('%Y%m%d')}_to_{week_end.strftime('%Y%m%d')}.txt"
            input_file = f"{claude_input_dir}/claude_input_{last_monday.strftime('%Y%m%d')}_to_{week_end.strftime('%Y%m%d')}.txt"
        else:
            # 对于非5天的情况，使用日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            output_file = f"{worklog_summary_dir}/worklog_summary_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.txt"
            input_file = f"{claude_input_dir}/claude_input_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.txt"

        return output_file, input_file

    def update_latest_symlink(self, output_file: str) -> bool:
        """
        更新latest_weekly_journal软链接指向最新报告

        Args:
            output_file: 最新的报告文件路径

        Returns:
            是否成功更新
        """
        try:
            symlink_path = os.path.join(os.path.dirname(__file__), "latest_weekly_journal")

            # 删除旧的软链接（如果存在）
            if os.path.exists(symlink_path):
                os.remove(symlink_path)

            # 创建新的软链接（使用相对路径）
            rel_path = os.path.relpath(output_file, os.path.dirname(__file__))
            os.symlink(rel_path, symlink_path)

            print(f"🔗 已更新软链接：latest_weekly_journal -> {os.path.basename(output_file)}")
            return True
        except Exception as e:
            print(f"⚠️  更新软链接失败: {e}")
            return False

    def generate_summary_with_claude(self, days: int = 5, use_claude: bool = True,
                                      prompt_file: str = "claude_analysis_prompt.md",
                                      output_file: str = None) -> str:
        """
        生成工作日志总结（可选自动调用Claude）

        Args:
            days: 统计天数
            use_claude: 是否使用Claude进行智能分析
            prompt_file: 分析提示词文件路径
            output_file: 输出文件路径，如果为None则自动生成

        Returns:
            总结内容
        """
        print(f"🔍 正在收集过去 {days} 天的工作日志...")

        # 收集日志
        log_files = self.find_recent_logs(days)

        if not log_files:
            print("❌ 未找到工作日志文件")
            return "未找到工作日志文件"

        print(f"✅ 找到 {len(log_files)} 个工作日志文件")

        logs = []
        for log_file in log_files:
            try:
                log_data = self.parse_log_file(log_file)
                logs.append(log_data)
            except Exception as e:
                print(f"  ⚠️  解析文件失败 {log_file}: {e}")

        # 收集原始内容（保存到文件）
        log_content = self.collect_logs_for_claude(days)

        # 自动生成文件名或使用提供的文件名
        if output_file is None:
            output_file, claude_input_file = self.generate_output_filename(days)
        else:
            # 如果提供了output_file，也生成对应的input_file
            _, claude_input_file = self.generate_output_filename(days)

        # 保存原始日志
        with open(claude_input_file, 'w', encoding='utf-8') as f:
            f.write(log_content)
        print(f"📄 原始日志内容已保存到：{claude_input_file}")

        # 调用Claude分析
        if use_claude:
            print("")
            analysis_result = self.call_claude_analysis(log_content, prompt_file)

            # 保存分析结果
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(analysis_result)

            print(f"📊 详细分析报告已保存到：{output_file}")

            # 自动更新软链接
            self.update_latest_symlink(output_file)

            return analysis_result
        else:
            return log_content


def main():
    """主函数"""
    import sys

    # 读取配置文件
    try:
        # 尝试从 config.py 读取配置
        sys.path.insert(0, os.path.dirname(__file__))
        from config import (
            WORKLOG_PATH, DEFAULT_DAYS, ENABLE_CLAUDE_BY_DEFAULT,
            CLAUDE_PROMPT_FILE, OUTPUT_FILE, CLAUDE_INPUT_FILE,
            CLAUDE_INPUT_DIR, WORKLOG_SUMMARY_DIR, AUTO_CREATE_DIRS, CLAUDE_PATH
        )

        # 验证 CLAUDE_PATH 是否存在
        if not os.path.exists(CLAUDE_PATH):
            print(f"⚠️  警告：CLAUDE_PATH 不存在 - {CLAUDE_PATH}")
            print("   请检查 config.py 中的 CLAUDE_PATH 配置")
            print("   获取路径方法：which claude")

        # 验证配置
        if WORKLOG_PATH == "/path/to/your/worklog":
            print("❌ 错误：请先配置工作日志路径")
            print("   请修改 config.py 中的 WORKLOG_PATH")
            return

        # 检查路径是否存在
        if not os.path.exists(WORKLOG_PATH):
            print(f"❌ 错误：路径不存在 - {WORKLOG_PATH}")
            print("   请检查 config.py 中的 WORKLOG_PATH 配置")
            return

        # 创建输出目录
        if AUTO_CREATE_DIRS:
            os.makedirs(CLAUDE_INPUT_DIR, exist_ok=True)
            os.makedirs(WORKLOG_SUMMARY_DIR, exist_ok=True)

    except ImportError:
        print("❌ 错误：找不到 config.py 配置文件")
        print("   请确保 config.py 文件存在并包含必要配置")
        return
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return

    # 创建收集器
    collector = WorklogCollector(WORKLOG_PATH)

    # 检查命令行参数
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            print("⚠️  错误：参数必须是数字")
            print("用法：python3 worklog_summarizer.py [天数] [--no-claude]")
            return
    else:
        days = DEFAULT_DAYS

    # 检查是否禁用Claude
    use_claude = ENABLE_CLAUDE_BY_DEFAULT
    if '--no-claude' in sys.argv:
        use_claude = False

    print("=" * 80)
    print("   工作日志自动总结工具")
    print("=" * 80)
    print("")

    # 计算工作周范围
    if days == 5:
        today = datetime.now()
        today_weekday = today.weekday()

        if today_weekday in [0, 1, 2, 3]:  # 周一到周四
            days_since_monday = today_weekday
            last_monday = today - timedelta(days=days_since_monday + 7)
        else:  # 周五到周日
            days_since_monday = today_weekday
            last_monday = today - timedelta(days=days_since_monday)

        week_end = last_monday + timedelta(days=4)  # 周五
        week_range = f"{last_monday.strftime('%Y-%m-%d')} 至 {week_end.strftime('%Y-%m-%d')}"
        print(f"📅 统计范围：{week_range}（完整工作周）")
    else:
        print(f"📅 统计范围：过去 {days} 天")

    print(f"🤖 Claude分析：{'开启' if use_claude else '关闭'}")
    print("")

    # 生成动态文件名
    output_file, input_file = collector.generate_output_filename(
        days,
        CLAUDE_INPUT_DIR,
        WORKLOG_SUMMARY_DIR
    )

    if use_claude:
        # 自动调用Claude生成完整分析
        result = collector.generate_summary_with_claude(
            days=days,
            use_claude=True,
            prompt_file=CLAUDE_PROMPT_FILE,
            output_file=output_file
        )

        print("")
        print("=" * 80)
        print("✅ 总结生成完成！")
        print("=" * 80)
        print("")
        print("📊 输出文件：")
        print(f"   1. 原始日志：{input_file}")
        print(f"   2. 分析报告：{output_file}")
        print("")
    else:
        # 仅收集日志，不调用Claude
        print(f"🔍 正在收集过去 {days} 天的工作日志...")
        log_content = collector.collect_logs_for_claude(days)

        # 保存原始日志
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(log_content)

        print(f"📄 原始日志内容已保存到：{input_file}")
        print("")
        print("=" * 80)
        print("✅ 收集完成！")
        print("")
        print("💡 使用方法：")
        print(f"   1. 查看日志内容：cat {input_file}")
        print(f"   2. 将文件内容复制并发送给Claude进行深度分析")
        print("   3. 或运行：python3 worklog_summarizer.py {days}  # 启用Claude分析")
        print("")


if __name__ == "__main__":
    main()