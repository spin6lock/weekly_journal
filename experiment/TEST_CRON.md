# 测试 Crontab 环境

## 问题说明

在 crontab 环境中运行时，PATH 环境变量通常只包含 `/usr/bin:/bin`，不包含 nvm 安装的 node 路径，导致 `claude` 脚本无法找到 `node` 命令。

## 修复方案

代码已经修复，现在会：
1. 自动从 `CLAUDE_PATH` 推断 `node` 的路径（适用于 nvm 安装）
2. 直接使用 `node` 执行 `claude` 脚本，避免依赖 shebang 和 PATH
3. 在环境变量中添加 node 路径，确保其他依赖也能正常工作

## 测试方法

### 方法1：使用测试脚本（推荐）

```bash
# 运行测试脚本，模拟 crontab 环境
./test_cron_simple.sh
```

这个脚本会：
- 设置最小 PATH（只有 `/usr/bin:/bin`）
- 运行工作日志总结脚本
- 验证修复是否有效

### 方法2：手动模拟 crontab 环境

```bash
# 设置最小 PATH（模拟 crontab）
export PATH="/usr/bin:/bin"

# 验证 node 和 claude 都找不到（这是预期的）
which node    # 应该返回空
which claude  # 应该返回空

# 运行脚本（使用 --no-claude 避免实际调用 Claude API）
python3 worklog_summarizer.py 1 --no-claude
```

### 方法3：实际测试调用 Claude

```bash
# 设置最小 PATH
export PATH="/usr/bin:/bin"

# 运行脚本（会实际调用 Claude，需要 API 密钥）
python3 worklog_summarizer.py 1
```

## 验证修复是否有效

如果修复成功，你应该看到：
- ✅ 脚本能够找到 node（即使 PATH 中没有）
- ✅ 脚本能够成功调用 claude
- ✅ 没有出现 "node: 没有那个文件或目录" 的错误

如果看到以下输出，说明修复有效：
```
🔧 已添加 node 路径到 PATH: /home/spin6lock/.nvm/versions/node/v22.17.0/bin
🔧 使用 node 直接执行 claude 脚本
```

## 在 Crontab 中使用

修复后，你可以在 crontab 中正常使用：

```bash
# 编辑 crontab
crontab -e

# 添加任务（示例：每周五下午 6 点运行）
0 18 * * 5 /home/spin6lock/opensource/weekly_journal/weekly_cron.sh
```

## 故障排除

如果仍然遇到问题：

1. **检查 CLAUDE_PATH 配置**
   ```bash
   # 查看 config.py 中的 CLAUDE_PATH
   grep CLAUDE_PATH config.py
   ```

2. **验证 node 路径**
   ```bash
   # 检查 node 是否在 claude 的同一目录下
   ls -la $(dirname $(grep CLAUDE_PATH config.py | cut -d'"' -f2))/node
   ```

3. **检查文件权限**
   ```bash
   # 确保 node 有执行权限
   ls -l /home/spin6lock/.nvm/versions/node/v22.17.0/bin/node
   ```

4. **查看详细错误信息**
   ```bash
   # 运行脚本并查看完整输出
   python3 worklog_summarizer.py 1 2>&1 | tee test_output.log
   ```
