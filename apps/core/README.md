# 核心功能模块 (Core App)

## 概述

`apps.core` 是一个通用功能模块，用于存放跨模块的管理命令和工具。

## 当前功能

### 1. 统一定时任务调度器

**命令**: `python manage.py run_all_scheduled_tasks`

**功能**: 同时调度 API 测试模块和 UI 自动化模块的定时任务

**支持的模块**:
- API 测试模块 (`apps.api_testing.models.ScheduledTask`)
- UI 自动化模块 (`apps.ui_automation.models.UiScheduledTask`)

### 2. 初始化元素定位策略

**命令**: `python manage.py init_locator_strategies`

**功能**: 初始化 UI 自动化测试的元素定位策略

**说明**: 此命令会创建/更新 12 种常用的元素定位策略，包括：
- 通用策略：ID, CSS, XPath, name, class, tag
- Playwright 专用策略：text, placeholder, role, label, title, test-id

### 3. 下载 WebDriver 驱动

**命令**: `python manage.py download_webdrivers`

**功能**: 预下载浏览器 WebDriver 驱动程序

**支持**:
- Chrome (ChromeDriver)
- Firefox (GeckoDriver)
- Edge (EdgeDriver)

**说明**: 首次使用 UI 自动化测试前建议先下载驱动，避免测试时等待下载

## 使用方法

### 1. 启动调度器（持续运行）

```bash
# 默认每60秒检查一次
python manage.py run_all_scheduled_tasks

# 自定义检查间隔（例如30秒）
python manage.py run_all_scheduled_tasks --interval 30
```

### 2. 单次执行模式

```bash
# 只执行一次检查，不循环
python manage.py run_all_scheduled_tasks --once
```

### 3. 初始化元素定位策略

```bash
# 初始化UI自动化的元素定位策略
python manage.py init_locator_strategies
```

**输出示例**:
```
开始初始化定位策略...
  ✓ 创建策略: ID
  ✓ 创建策略: CSS
  ✓ 创建策略: XPath
  - 策略已存在: name
  ...

============================================================
初始化完成！
新创建: 3 个
更新: 0 个
总计: 12 个定位策略
============================================================

当前可用的定位策略：
  - ID: 通过元素的 id 属性定位，最快速可靠
  - CSS: 通过 CSS 选择器定位，灵活强大
  - XPath: 通过 XPath 表达式定位，功能最强大
  ...
```

### 4. 下载 WebDriver 驱动

```bash
# 下载所有浏览器的驱动（默认）
python manage.py download_webdrivers

# 只下载指定浏览器的驱动
python manage.py download_webdrivers --browsers chrome firefox

# 只下载 Chrome 驱动
python manage.py download_webdrivers --browsers chrome
```

**输出示例**:
```
开始下载WebDriver驱动程序...
注意：首次下载可能需要几分钟时间

正在下载 ChromeDriver...
✓ ChromeDriver 下载成功 (耗时: 45.2秒)
  路径: /Users/xxx/.wdm/drivers/chromedriver/mac64/129.0.6668.58/chromedriver

正在下载 GeckoDriver (Firefox)...
✓ GeckoDriver 下载成功 (耗时: 32.1秒)
  路径: /Users/xxx/.wdm/drivers/geckodriver/mac64/v0.35.0/geckodriver

正在下载 EdgeDriver...
✓ EdgeDriver 下载成功 (耗时: 28.5秒)
  路径: /Users/xxx/.wdm/drivers/edgedriver/mac64/129.0.2792.65/edgedriver

============================================================
下载完成！成功: 3个
============================================================
驱动程序已缓存，后续测试执行将会更快！
```

**说明**:
- 首次下载可能需要几分钟，驱动会缓存到本地
- 后续执行测试时会自动使用缓存的驱动，无需重新下载
- 如果不预先下载，测试执行时会自动下载，但会增加测试等待时间

### 5. 生产环境部署建议

#### 方案1: 使用 systemd (推荐 Linux)

创建服务文件 `/etc/systemd/system/testhub-scheduler.service`:

```ini
[Unit]
Description=TestHub 统一定时任务调度器
After=network.target

[Service]
Type=simple
User=your_user
Group=your_group
WorkingDirectory=/path/to/testhub_platform
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python manage.py run_all_scheduled_tasks
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable testhub-scheduler
sudo systemctl start testhub-scheduler
sudo systemctl status testhub-scheduler
```

#### 方案2: 使用 Supervisor

配置文件 `/etc/supervisor/conf.d/testhub-scheduler.conf`:

```ini
[program:testhub-scheduler]
command=/path/to/venv/bin/python manage.py run_all_scheduled_tasks
directory=/path/to/testhub_platform
user=your_user
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/testhub-scheduler.log
```

启动:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start testhub-scheduler
```

#### 方案3: 使用 nohup (简单方式)

```bash
nohup python manage.py run_all_scheduled_tasks > logs/scheduler.log 2>&1 &
```

查看日志:
```bash
tail -f logs/scheduler.log
```

#### 方案4: 使用 screen 或 tmux

```bash
# 使用 screen
screen -S testhub-scheduler
python manage.py run_all_scheduled_tasks
# 按 Ctrl+A+D 分离会话

# 重新连接
screen -r testhub-scheduler

# 使用 tmux
tmux new-session -d -s testhub-scheduler 'python manage.py run_all_scheduled_tasks'
tmux attach-session -t testhub-scheduler
```

## 调度器输出示例

```
============================================================
启动统一定时任务调度器
检查间隔: 60秒
调度模块: API测试 + UI自动化
============================================================

[2026-01-10 23:30:00] 开始检查任务...
  [API] 执行任务: 每日接口测试
    ✓ 任务 每日接口测试 已启动
  [UI]  执行任务: 每周UI回归测试
    ✓ 任务 每周UI回归测试 已启动
✓ 本次调度执行了 2 个任务 (API: 1, UI: 1)
等待 60 秒后进行下一次检查...
```

## 与原有命令的对比

### 统一定时任务调度器

**旧命令（已弃用）**:
```bash
# 只能调度 API 测试任务
python manage.py run_scheduled_tasks
```

**新命令（推荐）**:
```bash
# 同时调度 API 测试和 UI 自动化任务
python manage.py run_all_scheduled_tasks
```

### 初始化元素定位策略

**旧命令位置**:
```bash
# 位于 apps/ui_automation/management/commands/
python manage.py init_locator_strategies
```

**新命令位置**:
```bash
# 位于 apps/core/management/commands/
python manage.py init_locator_strategies
```

**说明**: 命令功能完全相同，只是位置移到了 core 模块统一管理。

### 下载 WebDriver 驱动

**旧命令位置**:
```bash
# 位于 apps/ui_automation/management/commands/
python manage.py download_webdrivers
```

**新命令位置**:
```bash
# 位于 apps/core/management/commands/
python manage.py download_webdrivers
```

**说明**: 命令功能完全相同，只是位置移到了 core 模块统一管理。

## 注意事项

1. **不要同时运行多个调度器**: 确保同一时间只有一个调度器实例在运行，否则可能导致任务重复执行

2. **权限要求**: 调度器需要访问数据库和执行测试的权限，确保运行用户有足够的权限

3. **日志管理**: 建议将调度器输出重定向到日志文件，便于排查问题

4. **定时任务配置**: 定时任务需要在 Web 界面中配置，调度器只负责执行已配置的任务

5. **元素定位策略初始化**: 首次使用 UI 自动化测试功能前，建议先运行 `init_locator_strategies` 命令初始化定位策略

6. **WebDriver 预下载**: 首次使用 UI 自动化测试前，建议运行 `download_webdrivers` 命令预下载浏览器驱动，避免测试时等待下载

## 扩展说明

如果需要为其他模块添加定时任务调度功能，只需在 `run_all_scheduled_tasks.py` 中添加新的调度方法即可：

```python
def schedule_xxx_tasks(self):
    """调度 XXX 模块的定时任务"""
    # 实现类似 schedule_api_tasks 的逻辑
    pass
```

然后在 `handle()` 方法中调用：
```python
xxx_count = self.schedule_xxx_tasks()
```
