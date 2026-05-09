# Twitch 直播间关键词监控系统

## 项目简介
一个基于 PyQt6 和 Playwright 的 Twitch 直播间实时监控工具，支持关键词过滤、用户筛选、数据导出等功能。

## 技术栈

### 核心框架
- **Python 3.13+**：主开发语言
- **PyQt6**：GUI 界面框架，提供多标签页交互界面
- **Playwright (Python)**：浏览器自动化，用于网页抓取和交互

### 关键技术
- **浏览器自动化**：使用 Chromium 浏览器进行 Twitch 直播间访问
- **Cookie 注入**：手动导入浏览器 Cookie，绕过 Twitch 反自动化检测
- **DOM 提取**：通过 JavaScript 注入监听聊天消息变化
- **反检测机制**：
  - 移除 `--enable-automation` 参数
  - 注入 JS 隐藏 `navigator.webdriver`
  - 自定义 User-Agent
  - 模拟真实浏览器环境

### 数据处理
- **批量处理**：队列式缓存（10 条/批），减少磁盘 IO
- **关键词过滤**：实时匹配聊天消息中的关键词
- **用户名去重**：按用户名去重，保留首次出现记录
- **CSV 存储**：目标用户数据持久化到 CSV 文件
- **文本导出**：支持导出为格式化的 TXT 文件

### 国际化
- **i18n 系统**：基于 JSON 配置文件的动态语言切换
- **支持语言**：中文 (zh.json)、英文 (en.json)
- **实时切换**：无需重启，界面即时更新

### 打包工具
- **PyInstaller**：打包为独立可执行文件 (.exe)
- **一键运行**：无需安装 Python 环境

## 项目结构
```
twitch/
├── main.py                    # 主程序入口
├── modules/
│   ├── login_tab.py           # 登录管理模块
│   ├── keyword_manager_tab.py # 关键词管理模块
│   ├── live_monitor_tab.py    # 直播间监控模块
│   ├── target_users_tab.py    # 目标用户筛选模块
│   ├── i18n_manager.py        # 国际化管理器
│   └── keyword_manager.py     # 关键词数据管理
── i18n/
│   ├── zh.json                # 中文翻译
│   ── en.json                # 英文翻译
├── data/                      # 数据存储目录
│   ├── twitch_cookie.json     # Cookie 文件
│   ├── target_users.csv       # 目标用户数据
│   └── monitor_settings.json  # 监控设置
└── requirements.txt           # 依赖列表
```

## 核心功能
1. **登录管理**：手动导入 Cookie，携带登录状态
2. **关键词管理**：添加、删除、清空关键词
3. **实时监控**：输入直播间网址，实时提取聊天消息
4. **用户筛选**：自动过滤包含关键词的用户
5. **数据导出**：去重、导出为文本文件

## 运行环境
- Windows 10/11
- Python 3.13+
- 需要安装 Playwright 浏览器驱动

## 安装依赖
```bash
pip install -r requirements.txt
playwright install chromium
```

## 打包命令
```bash
pyinstaller --onefile --windowed --name="TwitchMonitor" --add-data "i18n;i18n" main.py
```

## 开源协议
MIT License

## 作者
Chase Qiu (永超·邱)
- QQ: 86609013
- Website: chaseqiu.top
