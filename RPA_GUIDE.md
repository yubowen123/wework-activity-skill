# RPA 自动化使用指南

企业微信活跃度管理系统 - RPA 自动化模块完整使用说明

## 📋 目录

1. [系统架构](#系统架构)
2. [快速开始](#快速开始)
3. [命令详解](#命令详解)
4. [配置说明](#配置说明)
5. [工作流程](#工作流程)
6. [常见问题](#常见问题)
7. [高级用法](#高级用法)

---

## 🏗️ 系统架构

RPA 模块包含以下核心组件:

- **wework_automation.py** - 企业微信客户端自动化控制
- **message_collector.py** - 消息采集器（从企业微信读取消息）
- **activity_analyzer.py** - 活跃度分析器（统计用户活跃度）
- **rule_executor.py** - 规则执行器（根据规则踢人）
- **scheduler.py** - 定时调度器（定时执行任务）
- **config.py** - 配置管理
- **main.py** - 命令行入口

---

## 🚀 快速开始

### 1. 启动 RPA 调度器（推荐）

最简单的使用方式，自动定时执行所有任务：

```bash
# 方式1：使用启动脚本（推荐）
./start_rpa.sh

# 方式2：直接运行
python -m rpa.main scheduler
```

调度器将：
- 每2小时自动采集一次消息
- 每天早上9点自动检查并执行规则

### 2. 手动采集消息

```bash
# 采集所有监控群聊的消息
python -m rpa.main collect

# 采集指定群聊
python -m rpa.main collect --chat "技术交流群"
```

### 3. 手动执行规则

```bash
# 模拟运行（不实际踢人，只查看结果）
python -m rpa.main execute --dry-run

# 实际执行（真正踢人）
python -m rpa.main execute

# 执行指定规则
python -m rpa.main execute --rule-id 1
```

---

## 📝 命令详解

### scheduler - 启动调度器

**作用**: 启动后台调度器，定时自动执行消息采集和规则检查

**用法**:
```bash
python -m rpa.main scheduler [--debug]
```

**选项**:
- `--debug` - 开启调试模式，保存截图和详细日志

**示例**:
```bash
# 普通模式
python -m rpa.main scheduler

# 调试模式
python -m rpa.main scheduler --debug
```

**运行后**:
- 按 Ctrl+C 停止

---

### collect - 采集消息

**作用**: 从企业微信采集群聊消息并存入数据库

**用法**:
```bash
python -m rpa.main collect [--chat 群聊名称] [--debug]
```

**选项**:
- `--chat` - 指定要采集的群聊名称（不指定则采集所有）
- `--debug` - 开启调试模式

**示例**:
```bash
# 采集所有监控群聊
python -m rpa.main collect

# 采集指定群聊
python -m rpa.main collect --chat "技术交流群"

# 调试模式采集
python -m rpa.main collect --chat "测试群" --debug
```

**注意事项**:
- 需要企业微信客户端已登录
- 确保群聊名称与企业微信中完全一致
- 首次使用建议开启 `--debug` 查看执行过程

---

### execute - 执行规则

**作用**: 检查并执行活跃度规则（标记/踢出不活跃用户）

**用法**:
```bash
python -m rpa.main execute [--dry-run] [--rule-id ID] [--debug]
```

**选项**:
- `--dry-run` - 模拟运行，不实际踢人（强烈推荐首次使用）
- `--rule-id` - 指定要执行的规则ID
- `--debug` - 开启调试模式

**示例**:
```bash
# 模拟运行所有规则（安全，推荐）
python -m rpa.main execute --dry-run

# 实际执行所有规则（谨慎使用）
python -m rpa.main execute

# 执行指定规则
python -m rpa.main execute --rule-id 1 --dry-run

# 调试模式
python -m rpa.main execute --dry-run --debug
```

**重要提示**:
- ⚠️ **首次使用务必加上 `--dry-run`** 查看会影响哪些用户
- 确认规则正确后再去掉 `--dry-run` 实际执行
- 白名单中的用户永远不会被踢出

---

### test - 测试自动化

**作用**: 测试企业微信自动化功能是否正常

**用法**:
```bash
python -m rpa.main test [--chat 群聊名称]
```

**示例**:
```bash
# 测试基本功能（启动、截图）
python -m rpa.main test

# 测试打开指定群聊
python -m rpa.main test --chat "测试群"
```

---

### import - 导入消息

**作用**: 从手动导出的文本文件导入消息记录

**用法**:
```bash
python -m rpa.main import --chat "群聊名称" --file "文件路径"
```

**文件格式要求**:
```
张三 10:30
这是一条消息

李四 11:45
这是另一条消息

王五 昨天 15:30
昨天的消息
```

消息之间用空行分隔。

**示例**:
```bash
python -m rpa.main import --chat "技术交流群" --file "./chat_history.txt"
```

---

### config - 查看配置

**作用**: 显示当前 RPA 配置

**用法**:
```bash
python -m rpa.main config
```

**输出示例**:
```
==================================================
RPA 配置:
==================================================
  api_base_url: http://localhost:8000
  debug: False
  message_collection_interval: 120
  rule_execution_time: 09:00
  rule_execution_dry_run: False
==================================================
```

---

## ⚙️ 配置说明

### 环境变量配置

可以通过环境变量自定义 RPA 行为：

```bash
# API 地址
export API_BASE_URL="http://localhost:8000"

# 开启调试模式
export RPA_DEBUG="true"

# 消息采集间隔（分钟）
export MESSAGE_COLLECTION_INTERVAL="120"

# 规则执行时间
export RULE_EXECUTION_TIME="09:00"

# 规则执行模式（true=模拟，false=实际）
export RULE_EXECUTION_DRY_RUN="true"

# 日志级别
export LOG_LEVEL="INFO"
```

### 修改配置文件

编辑 `rpa/config.py` 修改默认配置：

```python
# 消息采集间隔（分钟）
MESSAGE_COLLECTION_INTERVAL_MINUTES = 120  # 2小时

# 规则执行时间
RULE_EXECUTION_TIME = '09:00'  # 每天9点

# 是否模拟运行
RULE_EXECUTION_DRY_RUN = False  # True=模拟，False=实际
```

---

## 🔄 工作流程

### 典型使用流程

1. **初次设置** (在 Web 界面完成)
   - 添加要监控的群聊
   - 配置活跃度规则
   - 添加白名单用户

2. **测试 RPA 功能**
   ```bash
   # 测试企业微信自动化
   python -m rpa.main test --chat "测试群"
   ```

3. **手动导入历史消息** (可选)
   ```bash
   # 如果有历史聊天记录文件
   python -m rpa.main import --chat "技术交流群" --file chat.txt
   ```

4. **首次规则测试**
   ```bash
   # 模拟运行，查看哪些用户会被标记
   python -m rpa.main execute --dry-run
   ```

5. **启动自动化**
   ```bash
   # 启动调度器，进入自动化模式
   ./start_rpa.sh
   ```

### 日常运行

调度器启动后会：

**每2小时**:
- 自动采集所有监控群聊的新消息
- 更新数据库

**每天9点**:
- 检查所有活跃度规则
- 标记/踢出不符合规则的用户
- 记录执行日志

---

## ❓ 常见问题

### 1. RPA 无法启动企业微信

**原因**: 应用名称或 Bundle ID 不匹配

**解决**:
检查 `rpa/config.py` 中的配置：
```python
WEWORK_APP_NAME = "企业微信"  # 确保名称正确
WEWORK_BUNDLE_ID = "com.tencent.WeWorkMac"
```

### 2. 无法搜索到群聊

**原因**:
- 群聊名称不匹配
- 企业微信未登录

**解决**:
- 确保在 Web 界面添加的群聊名称与企业微信中完全一致
- 确保企业微信已登录

### 3. 消息采集失败

**当前状态**: 消息采集功能需要根据企业微信实际UI实现

**临时方案**:
1. 手动导出聊天记录
2. 使用 `import` 命令导入

```bash
python -m rpa.main import --chat "群名" --file "导出.txt"
```

### 4. 规则执行但没有踢人

**检查**:
1. 规则是否启用了"自动执行"
2. 是否在模拟运行模式 (`--dry-run`)
3. 用户是否在白名单中
4. 检查执行历史查看详细日志

### 5. 调度器停止了

**原因**:
- 系统睡眠
- 进程被终止

**解决**:
重新启动调度器：
```bash
./start_rpa.sh
```

### 6. 权限问题

**macOS 可能需要授予权限**:
- 系统偏好设置 → 安全性与隐私 → 辅助功能
- 添加终端或 Python 到允许列表

---

## 🔥 高级用法

### 自定义调度任务

编辑调度器创建自定义任务：

```python
from rpa.scheduler import RPAScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = RPAScheduler()

# 添加自定义任务：每天12点执行
def my_task():
    print("执行自定义任务")

scheduler.add_custom_job(
    func=my_task,
    trigger=CronTrigger(hour=12, minute=0),
    job_id="my_custom_task",
    name="我的任务"
)

scheduler.start()
```

### 集成到其他系统

RPA 模块可以作为 Python 包导入：

```python
from rpa import MessageCollector, RuleExecutor, ActivityAnalyzer

# 创建实例
collector = MessageCollector()
executor = RuleExecutor()
analyzer = ActivityAnalyzer()

# 采集消息
stats = collector.collect_all()

# 获取不活跃用户
inactive_users = analyzer.get_inactive_users(
    chat_id=1,
    inactive_days=7,
    min_messages_per_day=1
)

# 执行规则
results = executor.execute_all_rules(dry_run=True)
```

### 批量操作

```python
from rpa.message_collector import MessageCollector

collector = MessageCollector()

# 批量导入多个文件
chats = [
    ("技术交流群", "tech.txt"),
    ("产品讨论群", "product.txt"),
    ("设计团队", "design.txt")
]

for chat_name, file_path in chats:
    count = collector.import_from_text_file(chat_name, file_path)
    print(f"{chat_name}: 导入 {count} 条消息")
```

---

## 📊 监控和日志

### 查看执行历史

在 Web 界面 → 执行历史 页面查看：
- 每次规则执行的时间
- 受影响的用户
- 执行结果和错误信息

### 日志位置

RPA 日志输出到控制台，可以重定向保存：

```bash
# 保存日志到文件
python -m rpa.main scheduler > rpa.log 2>&1 &
```

### 调试模式

开启调试模式会：
- 保存每次操作的截图到 `debug_screenshots/` 目录
- 输出详细的执行日志
- 显示每个步骤的状态

```bash
python -m rpa.main scheduler --debug
```

---

## 🎯 最佳实践

1. **首次使用**
   - 先用 `--dry-run` 模拟运行
   - 检查白名单是否完整
   - 小范围测试后再全量使用

2. **规则设置**
   - 不要设置过于严格的规则
   - 给新成员留足适应时间
   - 定期review规则的合理性

3. **监控**
   - 定期查看执行历史
   - 关注异常情况
   - 及时调整规则

4. **备份**
   - 定期备份数据库文件 `data/wework.db`
   - 保存重要的聊天记录导出文件

5. **安全**
   - 谨慎使用自动踢人功能
   - 重要群聊建议只启用监控不启用自动踢人
   - 管理员账号加入白名单

---

## 🆘 获取帮助

```bash
# 查看帮助信息
python -m rpa.main --help

# 查看子命令帮助
python -m rpa.main collect --help
python -m rpa.main execute --help
```

---

**祝使用愉快！** 🎉
