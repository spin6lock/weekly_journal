# 工作周报定时生成和推送脚本

## 概述

`weekly_cron.sh` 是一个用于crontab的定时执行脚本，它会自动：
1. 生成过去7天的工作总结
2. 将总结推送到RocketChat的 #week_journal 频道

## 文件说明

- `weekly_cron.sh` - 主脚本文件（可执行）
- `crontab_example.txt` - Crontab配置示例
- `README_CRON.md` - 本说明文档

## 使用方法

### 1. 单独运行（测试）

```bash
/home/spin6lock/opensource/weekly_journal/weekly_cron.sh
```

### 2. 配置crontab（定时执行）

#### 查看当前crontab
```bash
crontab -l
```

#### 编辑crontab
```bash
crontab -e
```

#### 添加配置（每周一上午9点执行）
```bash
0 9 * * 1 /home/spin6lock/opensource/weekly_journal/weekly_cron.sh >> /home/spin6lock/opensource/weekly_journal/cron.log 2>&1
```

#### 或者直接加载配置
```bash
crontab /home/spin6lock/opensource/weekly_journal/crontab_example.txt
```

## 时间配置说明

| 时间 | crontab格式 | 说明 |
|------|-------------|------|
| 每天早上9点 | `0 9 * * *` | 每天执行 |
| 每周一早上9点 | `0 9 * * 1` | 每周一执行 |
| 每两周周一早上9点 | `0 9 1,15 * *` | 每月1号和15号执行 |
| 每月1号早上9点 | `0 9 1 * *` | 每月执行 |

格式说明：
```
秒 分 时 日 月 星期
*  *  *  *  *  *
│  │  │  │  │  │
│  │  │  │  │  └─── 星期几 (0 - 7) (0和7都表示星期日)
│  │  │  │  └────── 月份 (1 - 12)
│  │  │  └───────── 日期 (1 - 31)
│  │  └──────────── 小时 (0 - 23)
│  └─────────────── 分钟 (0 - 59)
└────────────────── 秒 (0 - 59, 可选)
```

## 日志查看

执行日志会保存到：
```bash
cat /home/spin6lock/opensource/weekly_journal/cron.log
```

实时查看：
```bash
tail -f /home/spin6lock/opensource/weekly_journal/cron.log
```

## 脚本工作流程

1. **生成周报**: 调用 `worklog_summarizer.py` 生成过去7天的工作总结
2. **查找文件**: 自动找到最新生成的报告文件（格式：`worklog_summary_*_to_*.txt`）
3. **推送到RocketChat**: 调用 `push_worklog.py` 将报告发送到 `#week_journal` 频道

## 依赖文件

脚本依赖以下文件：
- `/home/spin6lock/opensource/weekly_journal/worklog_summarizer.py`
- `/home/spin6lock/opensource/weekly_journal/config.py`
- `/home/spin6lock/opensource/push_to_rocketchat/push_worklog.py`
- `/home/spin6lock/opensource/push_to_rocketchat/config.py`

## 注意事项

1. 确保所有依赖文件存在且可执行
2. 确保工作日志目录路径配置正确（`/home/spin6lock/opensource/weekly_journal/config.py`）
3. 确保RocketChat配置正确（`/home/spin6lock/opensource/push_to_rocketchat/config.py`）
4. 脚本会生成详细的执行日志，便于问题排查

## 故障排查

如果脚本执行失败：

1. **检查日志**:
   ```bash
   cat /home/spin6lock/opensource/weekly_journal/cron.log
   ```

2. **手动执行测试**:
   ```bash
   /home/spin6lock/opensource/weekly_journal/weekly_cron.sh
   ```

3. **检查工作日志目录**:
   ```bash
   ls -la /home/spin6lock/docker_data/webdav/data/data/worklog/2025/11/
   ```

4. **检查配置文件**:
   ```bash
   cat /home/spin6lock/opensource/weekly_journal/config.py | grep WORKLOG_PATH
   cat /home/spin6lock/opensource/push_to_rocketchat/config.py
   ```

5. **检查Python依赖**:
   ```bash
   python3 -c "import sys; print(sys.path)"
   ```

## 联系信息

如有问题，请检查日志文件或联系系统管理员。