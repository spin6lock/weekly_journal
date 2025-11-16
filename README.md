# 📊 工作日志自动总结工具

一个结合 **Python数据收集** 与 **Claude智能分析** 的工作日志自动化分析工具，帮助您快速生成专业的周报和月度总结。

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![Claude](https://img.shields.io/badge/Claude-AI-orange.svg)](https://claude.ai/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ 核心特性

### 🤖 智能分析
- ✅ **Claude AI 深度分析** - 生成专业的工作总结、风险预警和改进建议
- ✅ **自动任务统计** - 智能识别已完成/待完成任务，计算完成率
- ✅ **工作分类统计** - 按主题自动分类工作内容
- ✅ **下周计划建议** - 基于当前进度推荐优先级

### 📁 智能收集
- ✅ **多种日期格式支持** - `YYYYMMDD.md`、`YYYYMMDD星期五.md`、`YYYYMMDD周X.md`
- ✅ **自动目录扫描** - 按年份/月份组织，自动发现日志文件
- ✅ **灵活时间范围** - 支持7天、30天或任意天数统计

### 💡 灵活使用
- ✅ **3种使用方式** - 命令行、交互脚本、Python模块
- ✅ **可自定义** - 支持自定义提示词、输出格式
- ✅ **零依赖** - 仅使用Python标准库

## 🚀 快速开始

### 准备工作

1. **确保已安装 Claude CLI**
   ```bash
   # 检查是否安装
   which claude

   # 如未安装，请访问 https://claude.ai 下载
   ```

2. **配置工作日志路径**
   ```bash
   # 复制配置模板
   cp config.py.example config.py

   # 编辑配置文件
   nano config.py  # 或使用其他编辑器
   # 修改 WORKLOG_PATH 为你的实际工作日志路径
   ```

3. **准备工作日志目录**
   ```
   worklog/
   └── 2025/
       ├── 11/
       │   ├── 20251110星期一.md
       │   ├── 20251111星期二.md
       │   └── ...
       └── 12/
   ```

3. **日志格式要求**
   ```markdown
   ## 需求
   - [x] 已完成任务1
   - [ ] 待完成任务

   ## 技术开发
   - [x] 实现功能A
   - [ ] 实现功能B
   ```

### 三种使用方式

#### 方式1：直接运行 Python 脚本（推荐⭐）

```bash
# 自动生成完整分析报告（调用Claude）
python3 worklog_summarizer.py

# 生成过去14天的工作总结
python3 worklog_summarizer.py 14

# 仅收集日志，不调用Claude
python3 worklog_summarizer.py 7 --no-claude
```

#### 方式2：使用便捷启动脚本

```bash
# 交互式运行（会提示输入天数）
./run_summary.sh

# 或直接指定天数
echo "14" | ./run_summary.sh
```

#### 方式3：导入 Python 模块使用

```python
from worklog_summarizer import WorklogCollector

# 创建收集器
collector = WorklogCollector("/path/to/your/worklog")

# 生成带Claude分析的总结
summary = collector.generate_summary_with_claude(
    days=30,
    use_claude=True,
    prompt_file="claude_analysis_prompt.md",
    output_file="monthly_report.txt"
)

# 查看结果
print(summary)
```

## 📝 工作日志格式要求

### 文件命名规范

- ✅ `20251107.md`
- ✅ `20251107星期五.md`
- ✅ `20251107周5.md`
- ✅ `20251107_其他文字.md`

### 任务标记格式

```markdown
## 计划
- [x] 已完成任务1
- [ ] 待完成任务

## 执行
- [x] 已完成任务2

## 检查
- [x] 已完成任务3
```

### 目录结构示例

```
worklog/
└── 2025/
    ├── 11/
    │   ├── 20251110星期一.md
    │   ├── 20251111星期二.md
    │   ├── 20251112星期三.md
    │   ├── 20251113星期四.md
    │   └── 20251114星期五.md
    └── 12/
        ├── 20251117星期一.md
        └── ...
```

## 💡 实际使用示例

### 示例1：自动生成周报（推荐）

```bash
$ python3 worklog_summarizer.py
================================================================================
   工作日志自动总结工具
================================================================================

📅 统计范围：过去 7 天
🤖 Claude分析：开启

🔍 正在收集过去 7 天的工作日志...
✅ 找到 5 个工作日志文件
🤖 正在调用Claude进行智能分析...
✅ Claude分析完成！
📊 详细分析报告已保存到：worklog_summary/worklog_summary_20251110_to_20251117.txt

✅ 总结生成完成！
```

**输出文件：**
- `claude_input/claude_input_20251110_to_20251117.txt` - 原始日志内容
- `worklog_summary/worklog_summary_20251110_to_20251117.txt` - **Claude智能分析报告**

### 示例2：仅收集日志（手动分析）

```bash
$ python3 worklog_summarizer.py 7 --no-claude

✅ 找到 5 个工作日志文件
📄 原始日志内容已保存到：claude_input/claude_input_20251110_to_20251117.txt

💡 使用方法：
   1. 查看日志内容：cat claude_input/claude_input_20251110_to_20251117.txt
   2. 将文件内容复制并发送给Claude进行深度分析
```

## 📊 Claude 分析报告样例

生成的报告包含以下内容：

### 📈 整体统计
- 统计周期：过去X天
- 日志天数：X天
- 总任务数：X项
- 已完成：X项
- 待完成：X项
- 完成率：X%

### 📊 工作分类统计
- 技术开发类：X次
- 配置与资产管理：X次
- 测试与联调：X次
- 文档与规划：X次

### ⭐ 关键成果与亮点
1. 成果1
   - 具体描述
2. 成果2

### ⚠️ 问题与风险
#### 未完成任务
1. 任务1（优先级：高/中/低）
   - 原因分析

#### 风险提示
- 风险1
- 风险2

### 💡 改进建议
#### 工作方法
- 建议1
- 建议2

### 📅 下周工作建议
#### 高优先级
1. 任务1
   - 预估时间：X小时
   - 关键依赖：XXX

## ⚙️ 自定义配置

### 1. 使用自定义分析提示词

创建 `my_prompt.md` 文件：

```python
collector.generate_summary_with_claude(
    days=7,
    prompt_file="my_prompt.md"  # 使用自定义提示词
)
```

### 2. 自定义输出文件名

```python
collector.generate_summary_with_claude(
    days=7,
    output_file="my_custom_report.txt"
)
```

### 3. 仅收集不分析

```python
collector.generate_summary_with_claude(
    days=7,
    use_claude=False  # 禁用Claude分析
)
```

### 4. 修改工作日志目录

编辑 `worklog_summarizer.py` 第615行：

```python
worklog_path = "/your/custom/worklog/path"
```

## 🎯 使用场景

### 场景1：周报生成
```bash
# 每周五运行
python3 worklog_summarizer.py 7

# → 生成专业的周报总结
```

### 场景2：月度回顾
```bash
# 月底运行
python3 worklog_summarizer.py 30

# → 生成月度分析报告
```

### 场景3：项目复盘
```bash
# 项目关键节点
python3 worklog_summarizer.py 14

# → 提供项目进展和风险分析
```

## 🆘 常见问题

**Q: Claude分析失败？**
A: 检查 `claude` 命令是否安装：`which claude`

**Q: 找不到工作日志文件？**
A: 请确保已在 config.py 中正确配置 WORKLOG_PATH，并确认目录存在

**Q: 如何配置工具？**
A: 使用以下步骤：
   1. 复制配置模板：`cp config.py.example config.py`
   2. 编辑配置文件：`nano config.py`（或使用其他编辑器）
   3. 修改 WORKLOG_PATH 为你的实际工作日志路径
   4. 保存并退出

**Q: 如何禁用 Claude 分析？**
A: 在 config.py 中设置 `ENABLE_CLAUDE_BY_DEFAULT = False`，或使用命令行参数 `--no-claude`

**Q: 任务解析不完整？**
A: 确保任务使用标准格式：`- [x] 任务内容`

**Q: 如何修改统计天数？**
A: 在命令行参数中指定：`python3 worklog_summarizer.py 14`

**Q: 脚本提示权限错误？**
A: 给脚本添加执行权限：`chmod +x run_summary.sh`

**Q: Claude分析太慢？**
A: 可使用 `--no-claude` 参数仅收集日志，手动分析

## 📈 效果对比

| 维度 | 传统手动统计 | 本工具 |
|------|-------------|--------|
| **效率** | 手动整理，耗时2-3小时 | 自动收集，耗时2分钟 |
| **准确性** | 容易遗漏和出错 | 完整准确，不遗漏 |
| **分析深度** | 基础统计 | AI深度分析 |
| **建议质量** | 主观判断 | 数据驱动，智能建议 |
| **可扩展性** | 难以复用 | 标准化流程，可复用 |

**效率提升：98%** 🚀

## 🎓 最佳实践

1. **日常记录**
   - 使用统一的任务标记格式
   - 每日及时更新状态
   - 补充Check和Act环节

2. **定期分析**
   - 每周五生成周报
   - 每月末生成月报
   - 项目关键节点复盘

3. **持续改进**
   - 根据Claude建议调整工作方式
   - 优化任务管理流程
   - 提升时间分配效率

## 📦 文件结构

```
weekly_journal/
├── worklog_summarizer.py          # 核心收集脚本
├── run_summary.sh                 # 便捷启动脚本
├── config.py                      # 配置文件（从 config.py.example 复制）
├── config.py.example              # 配置文件模板
├── .gitignore                     # Git忽略配置
├── claude_analysis_prompt.md      # Claude分析提示词
├── claude_input/                  # Claude输入文件目录（自动生成）
│   ├── claude_input_20251110_to_20251117.txt
│   └── ...
├── worklog_summary/               # 工作总结报告目录（自动生成）
│   ├── worklog_summary_20251110_to_20251117.txt
│   └── ...
└── README.md                      # 本文档
```

## 🛠️ 技术栈

- **Python 3.6+** - 核心开发语言
- **Claude CLI** - AI智能分析引擎
- **标准库** - 无外部依赖

## 📄 许可证

MIT

## 📞 获取帮助

- 📚 **快速入门**：查看上方文档
- 💡 **分析示例**：查看 `claude_analysis_example.md`
- 🤖 **Claude集成**：确保已安装 `claude` 命令行工具

---

**版本**：v2.0（Claude自动分析版）
**更新**：2025-11-17
**作者**：Claude Code（Anthropic）

⭐ 如果这个工具对您有帮助，请给它一个星标！