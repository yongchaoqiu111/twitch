"""""
Twitch 登录管理模块 - 使用 Playwright 实现登录和 Cookie 管理
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QGroupBox, QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from playwright.sync_api import sync_playwright
import json
import os


class TwitchLoginTab(QWidget):
    def __init__(self, data_dir, i18n=None):
        super().__init__()
        self.data_dir = data_dir
        self.i18n = i18n
        self.cookie_file = os.path.join(data_dir, "twitch_cookie.json")
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        self.title_label = QLabel(self.i18n.t("login_title") if self.i18n else "Twitch 登录管理")
        self.title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # 按钮组
        btn_layout = QHBoxLayout()
        
        self.btn_open = QPushButton(self.i18n.t("btn_open_twitch") if self.i18n else "打开 Twitch 登录页面")
        self.btn_open.setMinimumHeight(50)
        self.btn_open.clicked.connect(self.on_open_clicked)
        btn_layout.addWidget(self.btn_open)
        
        self.btn_save = QPushButton(self.i18n.t("btn_save_cookie") if self.i18n else "保存 Cookie")
        self.btn_save.setMinimumHeight(50)
        self.btn_save.clicked.connect(self.on_save_clicked)
        btn_layout.addWidget(self.btn_save)
        
        self.btn_load = QPushButton(self.i18n.t("btn_load_cookie") if self.i18n else "加载 Cookie 并登录")
        self.btn_load.setMinimumHeight(50)
        self.btn_load.clicked.connect(self.on_load_clicked)
        btn_layout.addWidget(self.btn_load)
        
        layout.addLayout(btn_layout)
        
        # 状态显示
        self.status_group = QGroupBox(self.i18n.t("status_group") if self.i18n else "状态信息")
        status_layout = QFormLayout()
        
        self.current_status_label = QLabel(self.i18n.t("not_started") if self.i18n else "未开始")
        status_layout.addRow(self.i18n.t("current_status") if self.i18n else "当前状态:", self.current_status_label)
        
        self.current_action_label = QLabel(self.i18n.t("waiting_start") if self.i18n else "等待操作")
        status_layout.addRow(self.i18n.t("current_action") if self.i18n else "当前动作:", self.current_action_label)
        
        self.status_group.setLayout(status_layout)
        layout.addWidget(self.status_group)
        
        # 消息显示
        self.message_label = QLabel("")
        self.message_label.setStyleSheet("color: green; padding: 10px; font-size: 12px;")
        layout.addWidget(self.message_label)
        
        layout.addStretch()
    
    def update_language(self):
        """更新语言"""
        if not self.i18n:
            return
        
        self.title_label.setText(self.i18n.t("login_title"))
        self.btn_open.setText(self.i18n.t("btn_open_twitch"))
        self.btn_save.setText(self.i18n.t("btn_save_cookie"))
        self.btn_load.setText(self.i18n.t("btn_load_cookie"))
        self.status_group.setTitle(self.i18n.t("status_group"))
        self.current_status_label.setText(self.i18n.t("current_status"))
        self.current_action_label.setText(self.i18n.t("current_action"))
    
    def on_open_clicked(self):
        self.show_message("正在打开 Twitch...", "blue")
        self.current_status_label.setText(self.i18n.t("running"))
        self.current_status_label.setStyleSheet("color: green;")
        
        try:
            # 先清理旧的资源
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=False,
                channel='chrome',
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--start-maximized'
                ],
                ignore_default_args=['--enable-automation']
            )

            # 关键：删除 navigator.webdriver 标志
            context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
            )

            # 注入 JS 永久过检测
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
            """)
            
            self.context = context
            self.page = context.new_page()
            self.page.goto('https://www.twitch.tv/login', wait_until='domcontentloaded', timeout=60000)
            
            self.show_message("请在浏览器中完成登录", "green")
            self.current_status_label.setText(self.i18n.t("waiting_login"))
            self.current_action_label.setText(self.i18n.t("action_login"))
            
        except Exception as e:
            if 'Timeout' in str(e) or 'timeout' in str(e):
                self.show_message("请在浏览器中完成登录", "green")
                self.current_status_label.setText(self.i18n.t("waiting_login"))
                self.current_action_label.setText(self.i18n.t("action_login"))
            else:
                self.show_message(f"错误: {str(e)}", "red")
                self.current_status_label.setText(self.i18n.t("failed"))
    
    def on_save_clicked(self):
        if not self.page:
            self.show_message("请先打开浏览器", "red")
            return
        
        self.show_message("正在保存 Cookie...", "blue")
        self.current_status_label.setText(self.i18n.t("running"))
        
        try:
            cookies = self.page.context.cookies()
            
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            
            self.show_message(f"Cookie 已保存，共 {len(cookies)} 条", "green")
            self.current_status_label.setText(self.i18n.t("completed"))
            self.current_action_label.setText(self.i18n.t("action_saved", count=len(cookies)))
            
        except Exception as e:
            self.show_message(f"保存失败: {str(e)}", "red")
            self.current_status_label.setText(self.i18n.t("failed"))
    
    def on_load_clicked(self):
        if not os.path.exists(self.cookie_file):
            self.show_message("Cookie 文件不存在，请先保存", "red")
            return
        
        self.show_message("正在加载 Cookie...", "blue")
        self.current_status_label.setText(self.i18n.t("running"))
        
        try:
            # 先清理旧的资源
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=False,
                channel='chrome',
                args=['--start-maximized']
            )
            
            self.context = self.browser.new_context()
            self.context.add_cookies(cookies)
            self.page = self.context.new_page()
            self.page.goto('https://www.twitch.tv', wait_until='domcontentloaded', timeout=60000)
            
            self.show_message("Cookie 加载成功", "green")
            self.current_status_label.setText(self.i18n.t("completed"))
            self.current_action_label.setText(self.i18n.t("action_cookie_login"))
            
        except Exception as e:
            if 'Timeout' in str(e) or 'timeout' in str(e):
                self.show_message("浏览器已打开，请检查登录状态", "green")
                self.current_status_label.setText(self.i18n.t("completed"))
            else:
                self.show_message(f"错误: {str(e)}", "red")
                self.current_status_label.setText(self.i18n.t("failed"))
    
    def show_message(self, text, color):
        self.message_label.setText(text)
        self.message_label.setStyleSheet(f"color: {color}; padding: 10px; font-size: 12px;")
    
    def closeEvent(self, event):
        """清理资源"""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except:
            pass
        super().closeEvent(event)
