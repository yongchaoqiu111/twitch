"""
直播间监控 Tab - 输入网址、选择关键词并开始提取聊天记录
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QGroupBox, QTextEdit, QLineEdit, QListWidget,
                             QListWidgetItem, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from modules.keyword_manager import KeywordManager
from playwright.sync_api import sync_playwright
import json
import os
import time
from datetime import datetime
import csv


class MonitorWorker(QThread):
    """监控工作线程"""
    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    user_found_signal = pyqtSignal(dict) # 发送找到的用户信息
    
    def __init__(self, url, keywords, cookie_file, data_dir):
        super().__init__()
        self.url = url
        self.keywords = [k.lower() for k in keywords]
        self.cookie_file = cookie_file
        self.data_dir = data_dir
        self.is_running = True
        self.user_queue = []  # 用户数据队列
        self.batch_size = 10  # 每10条数据写入一次（测试用）
        
    def run(self):
        try:
            self.status_signal.emit("正在启动浏览器...")
            playwright = sync_playwright().start()
            
            browser = playwright.chromium.launch(
                headless=False,
                channel='chrome',
                args=['--start-maximized']
            )
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            
            self.status_signal.emit(f"正在进入直播间: {self.url}")
            page.goto(self.url, wait_until='domcontentloaded', timeout=120000)
            
            # 等待页面完全加载（开代理需要更长延迟）
            self.log_signal.emit("等待页面加载...（30秒）")
            time.sleep(30)
            self.log_signal.emit("已进入直播间，开始监控聊天...")
            self.status_signal.emit("监控中...")
            
            # 监听聊天消息（通过 JavaScript 注入）
            page.evaluate("""
                () => {
                    window.chatMessages = [];
                    
                    // 使用正确的聊天容器选择器
                    const chatContainer = document.querySelector('[data-test-selector="chat-room-component-layout"]');
                    
                    if (chatContainer) {
                        const observer = new MutationObserver((mutations) => {
                            mutations.forEach((mutation) => {
                                mutation.addedNodes.forEach((node) => {
                                    if (node.nodeType === 1) {
                                        // 查找所有聊天消息行
                                        const chatLines = node.getAttribute('class')?.includes('chat-line__message')
                                            ? [node]
                                            : node.querySelectorAll ? Array.from(node.querySelectorAll('.chat-line__message')) : [];
                                        
                                        chatLines.forEach((chatLine) => {
                                            // 提取用户名 - 从 data-a-user 属性
                                            const username = chatLine.getAttribute('data-a-user') || 'Unknown';
                                            
                                            // 提取消息内容 - 从 .text-fragment
                                            const textFragment = chatLine.querySelector('.text-fragment');
                                            const message = textFragment ? textFragment.textContent.trim() : '';
                                            
                                            if (message) {
                                                window.chatMessages.push({user: username, message, time: Date.now()});
                                            }
                                        });
                                    }
                                });
                            });
                        });
                        observer.observe(chatContainer, { childList: true, subtree: true });
                    }
                }
            """)
            
            while self.is_running:
                messages = page.evaluate("() => window.chatMessages || []")
                page.evaluate("() => window.chatMessages = []")
                
                for msg in messages:
                    user = msg.get('user', 'Unknown')
                    text = msg.get('message', '')
                    
                    # 实时显示日志
                    result = f"[{user}] {text}"
                    self.log_signal.emit(result)
                    
                    # 捕获所有消息到队列（用于后续批量保存）
                    user_info = {
                        'username': user,
                        'profile_url': f"https://www.twitch.tv/{user}",
                        'message': text,
                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.user_queue.append(user_info)
                
                # 批量处理：达到100条时过滤、去重、保存到CSV
                if len(self.user_queue) >= self.batch_size:
                    self._batch_save_users()
                
                time.sleep(1)
            
            context.close()
            playwright.stop()
            
        except Exception as e:
            self.status_signal.emit(f"错误: {str(e)}")
            self.log_signal.emit(f"发生错误: {str(e)}")
    
    def stop(self):
        self.is_running = False
    
    def _batch_save_users(self):
        """批量处理：过滤关键词、去重用户名、写入CSV"""
        if not self.user_queue:
            return
        
        # 1. 过滤关键词
        filtered_users = []
        for user_info in self.user_queue:
            text = user_info.get('message', '').lower()
            
            # 如果未设置关键词，保留所有；否则只保留匹配的
            if not self.keywords:
                matched_keywords = '全部'
            else:
                matched = [kw for kw in self.keywords if kw in text]
                if not matched:
                    continue  # 不匹配则跳过
                matched_keywords = ', '.join(matched)
            
            filtered_users.append({
                'username': user_info['username'],
                'profile_url': user_info['profile_url'],
                'keywords': matched_keywords,
                'time': user_info['time']
            })
        
        # 2. 去重（按用户名）
        seen_users = set()
        unique_users = []
        for user_info in filtered_users:
            username = user_info['username']
            if username not in seen_users:
                seen_users.add(username)
                unique_users.append(user_info)
        
        # 3. 批量写入CSV
        if unique_users:
            csv_path = os.path.join(self.data_dir, "target_users.csv")
            file_exists = os.path.exists(csv_path)
            
            with open(csv_path, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=['username', 'profile_url', 'keywords', 'time'])
                if not file_exists:
                    writer.writeheader()
                writer.writerows(unique_users)
            
            self.log_signal.emit(f"✅ 批量保存 {len(unique_users)} 个用户（已去重）")
        
        # 清空队列
        self.user_queue.clear()


class LiveMonitorTab(QWidget):
    def __init__(self, data_dir, i18n=None):
        super().__init__()
        self.data_dir = data_dir
        self.i18n = i18n
        self.cookie_file = os.path.join(data_dir, "twitch_cookie.json")
        self.keyword_manager = KeywordManager(data_dir)
        self.worker = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        self.title_label = QLabel(self.i18n.t("monitor_title") if self.i18n else "直播间关键词监控")
        self.title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # 输入区域
        self.input_group = QGroupBox(self.i18n.t("monitor_settings_group") if self.i18n else "监控设置")
        input_layout = QVBoxLayout()
        
        # 直播间网址（带历史记录下拉）
        url_layout = QHBoxLayout()
        self.url_label = QLabel(self.i18n.t("live_url_label") if self.i18n else "直播间网址:")
        url_layout.addWidget(self.url_label)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(self.i18n.t("live_url_placeholder") if self.i18n else "例如: https://www.twitch.tv/shroud")
        url_layout.addWidget(self.url_input)
        
        # 历史记录下拉框
        self.url_history = QListWidget()
        self.url_history.setMaximumHeight(80)
        self.url_history.itemClicked.connect(self.on_url_selected)
        url_layout.addWidget(self.url_history)
        
        input_layout.addLayout(url_layout)
        
        # 加载保存的设置
        self.load_settings()
        
        # 关键词选择
        keyword_layout = QHBoxLayout()
        self.keyword_select_label = QLabel(self.i18n.t("select_keywords_label") if self.i18n else "选择关键词:")
        keyword_layout.addWidget(self.keyword_select_label)
        self.keyword_list = QListWidget()
        self.keyword_list.setMaximumHeight(100)
        self.load_keywords()
        keyword_layout.addWidget(self.keyword_list)
        input_layout.addLayout(keyword_layout)
        
        # 控制按钮
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton(self.i18n.t("btn_refresh_keywords") if self.i18n else "刷新关键词")
        self.btn_refresh.clicked.connect(self.load_keywords)
        btn_layout.addWidget(self.btn_refresh)
        
        self.btn_start = QPushButton(self.i18n.t("btn_start_monitor") if self.i18n else "开始监控")
        self.btn_start.setMinimumHeight(40)
        self.btn_start.clicked.connect(self.start_monitoring)
        btn_layout.addWidget(self.btn_start)
        
        self.btn_stop = QPushButton(self.i18n.t("btn_stop_monitor") if self.i18n else "停止监控")
        self.btn_stop.setMinimumHeight(40)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_monitoring)
        btn_layout.addWidget(self.btn_stop)
        
        input_layout.addLayout(btn_layout)
        self.input_group.setLayout(input_layout)
        layout.addWidget(self.input_group)
        
        # 状态显示
        self.status_label = QLabel(self.i18n.t("status_label") if self.i18n else "状态: 未开始")
        layout.addWidget(self.status_label)
        
        # 日志显示
        self.log_group = QGroupBox(self.i18n.t("log_group") if self.i18n else "实时监控日志")
        log_layout = QVBoxLayout()
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        log_layout.addWidget(self.log_display)
        self.log_group.setLayout(log_layout)
        layout.addWidget(self.log_group)
        
        layout.addStretch()
    
    def update_language(self):
        """更新界面语言"""
        if not self.i18n:
            return
        
        self.title_label.setText(self.i18n.t("monitor_title"))
        self.input_group.setTitle(self.i18n.t("monitor_settings_group"))
        self.url_label.setText(self.i18n.t("live_url_label"))
        self.url_input.setPlaceholderText(self.i18n.t("live_url_placeholder"))
        self.keyword_select_label.setText(self.i18n.t("select_keywords_label"))
        self.btn_refresh.setText(self.i18n.t("btn_refresh_keywords"))
        self.btn_start.setText(self.i18n.t("btn_start_monitor"))
        self.btn_stop.setText(self.i18n.t("btn_stop_monitor"))
        self.log_group.setTitle(self.i18n.t("log_group"))
        
        # 更新状态标签（根据当前状态）
        current_status = self.status_label.text()
        if "错误" in current_status or "Error" in current_status:
            pass # 保持错误信息不变，或者可以重新翻译前缀
        elif "已停止" in current_status or "Stopped" in current_status:
            self.status_label.setText(self.i18n.t("msg_monitor_stopped"))
        else:
            self.status_label.setText(self.i18n.t("status_label"))

    def load_keywords(self):
        """加载关键词列表"""
        self.keyword_list.clear()
        # 重新从文件加载
        self.keyword_manager.load_keywords()
        keywords = self.keyword_manager.get_keywords()
        for kw in keywords:
            item = QListWidgetItem(kw)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.keyword_list.addItem(item)
    
    def get_selected_keywords(self):
        """获取选中的关键词"""
        selected = []
        for i in range(self.keyword_list.count()):
            item = self.keyword_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        return selected
    
    def start_monitoring(self):
        # 每次开始前自动刷新关键词列表，确保获取最新数据
        self.load_keywords()
        
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "警告", "请输入直播间网址")
            return
        
        keywords = self.get_selected_keywords()
        # 如果未选择关键词，默认全选
        if not keywords:
            for i in range(self.keyword_list.count()):
                item = self.keyword_list.item(i)
                item.setCheckState(Qt.CheckState.Checked)
            keywords = self.get_selected_keywords()
        
        if not os.path.exists(self.cookie_file):
            reply = QMessageBox.question(self, "提示", "未检测到登录 Cookie，是否继续？\n（可能无法访问某些直播间）",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
        
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.status_label.setText("状态: 正在启动...")
        self.status_label.setStyleSheet("color: blue;")
        
        self.worker = MonitorWorker(url, keywords, self.cookie_file, self.data_dir)
        self.worker.log_signal.connect(self.log_display.append)
        self.worker.status_signal.connect(self.update_status)
        self.worker.user_found_signal.connect(self.on_user_found)
        self.worker.start()
    
    def stop_monitoring(self):
        self.save_settings() # 停止时保存设置
        if self.worker:
            self.worker.stop()
            self.worker.wait()
        
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.status_label.setText("状态: 已停止")
        self.status_label.setStyleSheet("color: red;")
        self.log_display.append("--- 监控已停止 ---")
    
    def update_status(self, status):
        self.status_label.setText(f"状态: {status}")
        if "错误" in status:
            self.status_label.setStyleSheet("color: red;")
        else:
            self.status_label.setStyleSheet("color: green;")

    def on_user_found(self, user_info):
        """当监控线程找到目标用户时，保存到文件并通知主界面"""
        # 保存到 CSV
        csv_path = os.path.join(self.data_dir, "target_users.csv")
        file_exists = os.path.exists(csv_path)
        
        with open(csv_path, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['username', 'profile_url', 'keywords', 'time'])
            if not file_exists:
                writer.writeheader()
            writer.writerow(user_info)
        
        # 这里可以触发主界面的表格刷新信号（后续在 main.py 中连接）

    def load_settings(self):
        """加载保存的网址历史"""
        settings_file = os.path.join(self.data_dir, "monitor_settings.json")
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if 'last_urls' in settings and settings['last_urls']:
                        # 显示历史记录
                        self.url_history.clear()
                        for url in settings['last_urls']:
                            item = QListWidgetItem(url)
                            self.url_history.addItem(item)
                        # 复用上次最后一条网址
                        self.url_input.setText(settings['last_urls'][0])
            except:
                pass
    
    def on_url_selected(self, item):
        """点击历史网址时填充到输入框"""
        self.url_input.setText(item.text())

    def save_settings(self):
        """保存当前的网址到历史记录"""
        url = self.url_input.text().strip()
        if not url:
            return
            
        settings_file = os.path.join(self.data_dir, "monitor_settings.json")
        settings = {'last_urls': []}
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            except:
                pass
        
        # 保持最近3个记录
        if url in settings['last_urls']:
            settings['last_urls'].remove(url)
        settings['last_urls'].insert(0, url)
        settings['last_urls'] = settings['last_urls'][:3]
        
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
