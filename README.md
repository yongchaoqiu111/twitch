# Twitch 直播间关键词监控系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.x-green.svg)
![Playwright](https://img.shields.io/badge/Playwright-Automation-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**实时监控 Twitch 直播间聊天，智能筛选目标用户**

[功能特点](#功能特点) • [快速开始](#快速开始) • [使用说明](#使用说明) • [技术架构](#技术架构) • [开源协议](#开源协议)

</div>

---

## 功能特点

### 🎯 核心功能
- **直播间实时监控**：自动提取直播间聊天消息
- **关键词智能过滤**：精准匹配聊天内容中的关键词
- **目标用户筛选**：自动识别并记录匹配用户
- **用户名去重**：一键去重，保留首次出现记录
- **数据导出**：支持导出为格式化文本文件

### 🌐 国际化支持
- **中英双语**：一键切换界面语言
- **实时切换**：无需重启，即时生效

### 🛡️ 反检测机制
- **Cookie 注入**：手动导入浏览器 Cookie，绕过自动化检测
- **隐藏自动化特征**：移除 webdriver 标志，模拟真实浏览器
- **稳定可靠**：长时间监控不掉线

### 💾 高效处理
- **批量写入**：队列式缓存，减少磁盘 IO
- **实时日志**：监控过程可视化
- **历史记录**：自动保存最近使用的直播间网址

---

## 快速开始

### 环境要求
- **操作系统**：Windows 10/11
- **Python**：3.13 或更高版本
- **浏览器**：Google Chrome 或 Microsoft Edge

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/yourusername/twitch-monitor.git
cd twitch-monitor
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **安装浏览器驱动**
```bash
playwright install chromium
```

4. **运行程序**
```bash
python main.py
```

### 打包为 EXE（可选）
```bash
pyinstaller --onefile --windowed --name="TwitchMonitor" --add-data "i18n;i18n" main.py
```
打包后的文件位于 `dist/TwitchMonitor.exe`

---

## 使用说明

### 1️⃣ 登录管理
1. 点击**打开 Twitch**，在浏览器中手动登录账号
2. 点击**保存 Cookie**，将登录状态保存到本地
3. 下次使用时点击**加载 Cookie 并登录**即可快速进入

### 2️⃣ 关键词管理
1. 在输入框中输入关键词，点击**添加**
2. 支持添加多个关键词，用于筛选聊天消息
3. 可删除单个关键词或清空全部

### 3️⃣ 直播间监控
1. 输入 Twitch 直播间网址（支持历史记录快速选择）
2. 勾选需要监控的关键词
3. 点击**开始监控**，等待 30 秒页面加载
4. 系统自动提取聊天消息，实时显示在日志中
5. 每 10 条消息自动过滤、去重、保存

### 4️⃣ 目标用户筛选
1. 切换到**目标用户筛选**标签页
2. 点击**刷新列表**查看已保存的用户
3. 点击**去重**按钮清理重复用户名
4. 点击**导出到文本**将数据导出为 `.txt` 文件

---

## 技术架构

### 核心框架
- **Python 3.13+**：主开发语言
- **PyQt6**：现代化 GUI 界面框架
- **Playwright**：浏览器自动化与网页抓取

### 关键技术
- **DOM 提取**：通过 `MutationObserver` 监听聊天容器变化
- **JavaScript 注入**：实时捕获聊天消息
- **Cookie 管理**：手动导入 + 自动注入
- **批量处理**：内存队列缓存，减少文件 IO

### 项目结构
```
twitch-monitor/
├── main.py                      # 主程序入口
├── modules/
│   ├── login_tab.py             # 登录管理模块
│   ├── keyword_manager_tab.py   # 关键词管理模块
│   ├── live_monitor_tab.py      # 直播间监控模块
│   ├── target_users_tab.py      # 目标用户筛选模块
│   ├── i18n_manager.py          # 国际化管理器
│   └── keyword_manager.py       # 关键词数据管理
├── i18n/
│   ├── zh.json                  # 中文翻译
│   └── en.json                  # 英文翻译
├── data/                        # 数据存储目录
│   ├── twitch_cookie.json       # Cookie 文件
│   ├── target_users.csv         # 目标用户数据
│   └── monitor_settings.json    # 监控设置
├── dist/                        # 打包输出目录
│   └── TwitchMonitor.exe        # 可执行文件
├── requirements.txt             # 依赖列表
├── TECH_STACK.md                # 技术栈文档
└── README.md                    # 项目说明
```

---

## 注意事项

### ️ 使用须知
1. **Cookie 安全**：Cookie 文件包含登录信息，请妥善保管
2. **监控频率**：建议控制监控时长，避免频繁请求
3. **网络环境**：建议使用稳定的网络连接或代理
4. **合规使用**：请遵守 Twitch 平台服务条款，合理使用本工具

### 🔧 常见问题
- **无法提取聊天消息**：等待 30 秒页面加载，确保直播间有聊天活动
- **Cookie 失效**：重新打开 Twitch 并登录，再次保存 Cookie
- **窗口未显示**：检查任务栏是否有 Python 图标，或按 `Alt + Tab` 切换

---

## 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

你可以自由使用、修改和分发本项目，但需保留原始版权声明。

---

## 👤 作者

**Chase Qiu (永超·邱)**

### 专业背景
专注企业级AI系统架构设计、大模型落地、RAG/Agent工程化开发实战干货。

### 合作方向
- **架构咨询**：AI系统架构设计与技术选型
- **项目搭案**：从0到1的AI项目搭建与实施  
- **技术方案输出**：定制化技术解决方案

### 联系方式
- **QQ**: 86609013
- **主页**: [ChaseQiu.top](https://chaseqiu.top)
- **私信说明需求，可获取初步思路**

---

## ⚖️ 免责声明

**Disclaimer**: This tool is for educational and research purposes only. Users are responsible for complying with Twitch's Terms of Service and applicable laws.

**免责声明**: 本工具仅用于教育和研究目的。使用者需自行遵守 Twitch 平台服务条款和适用法律法规。

---

## 支持项目

如果这个项目对你有帮助，欢迎：
- ⭐ Star 本项目
- 🍴 Fork 并贡献代码
- 🐛 提交 Issue 反馈问题
- 💡 提出改进建议

---

<div align="center">

**Made with ❤️ by Chase Qiu**

[⬆ 返回顶部](#twitch-直播间关键词监控系统)

</div>
