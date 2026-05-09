import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QCheckBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# 添加modules目录到sys.path
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

modules_path = os.path.join(application_path, 'modules')
if os.path.exists(modules_path) and modules_path not in sys.path:
    sys.path.insert(0, application_path)

from modules.login_tab import TwitchLoginTab
from modules.keyword_manager_tab import KeywordManagerTab
from modules.live_monitor_tab import LiveMonitorTab
from modules.target_users_tab import TargetUsersTab
from modules.i18n_manager import I18nManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.i18n = I18nManager()
        self.update_window_title()
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.raise_()
        self.activateWindow()
        
        # 设置数据目录
        if getattr(sys, 'frozen', False):
            self.data_dir = os.path.join(os.path.dirname(sys.executable), 'data')
        else:
            self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 初始化UI
        self.init_ui()
    
    def update_window_title(self):
        """更新窗口标题"""
        self.setWindowTitle(self.i18n.t("app_title"))
    
    def init_ui(self):
        """初始化用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. 广告栏
        self.author_bar = QLabel(self.i18n.t("author_bar"))
        self.author_bar.setStyleSheet("""
            QLabel {
                background-color: #2C3E50;
                color: white;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
                text-align: center;
            }
        """)
        self.author_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.author_bar)
        
        # 2. 语言切换开关
        lang_layout = QHBoxLayout()
        lang_layout.setContentsMargins(10, 8, 10, 5)
        
        self.lang_switch = QCheckBox(self.i18n.t("lang_en"))
        self.lang_switch.setFixedSize(100, 35)
        self.lang_switch.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                font-weight: bold;
                color: #2C3E50;
            }
            QCheckBox::indicator {
                width: 40px;
                height: 20px;
                border-radius: 10px;
                background-color: #27AE60;
            }
            QCheckBox::indicator:unchecked {
                background-color: #BDC3C7;
            }
        """)
        self.lang_switch.toggled.connect(self.on_lang_switch_toggled)
        lang_layout.addWidget(self.lang_switch)
        lang_layout.addStretch()
        main_layout.addLayout(lang_layout)
        
        # 3. Tab控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(QFont("Microsoft YaHei", 10))
        
        # 添加各个功能Tab
        self.login_tab = TwitchLoginTab(self.data_dir, self.i18n)
        self.keyword_tab = KeywordManagerTab(self.data_dir, self.i18n)
        self.monitor_tab = LiveMonitorTab(self.data_dir, self.i18n)
        self.target_users_tab = TargetUsersTab(self.data_dir, self.i18n)
        
        # 保存Tab引用以便后续更新
        self.tabs = [
            ("tab_login", self.login_tab),
            ("tab_keyword", self.keyword_tab),
            ("tab_monitor", self.monitor_tab),
            ("tab_target_users", self.target_users_tab)
        ]
        
        # 将Tab添加到tab_widget
        for key, tab in self.tabs:
            self.tab_widget.addTab(tab, self.i18n.t(key))
        
        self.update_tab_labels()
        main_layout.addWidget(self.tab_widget)
    
    def update_tab_labels(self):
        """更新Tab标签"""
        tab_keys = ["tab_login", "tab_keyword", "tab_monitor", "tab_target_users"]
        for i, key in enumerate(tab_keys):
            self.tab_widget.setTabText(i, self.i18n.t(key))
    
    def on_lang_switch_toggled(self, checked):
        """语言开关切换"""
        lang_code = "en" if checked else "zh"
        self.switch_language(lang_code)
    
    def switch_language(self, lang_code):
        """切换语言"""
        if self.i18n.set_language(lang_code):
            # 更新窗口标题
            self.update_window_title()
            # 更新广告栏
            self.author_bar.setText(self.i18n.t("author_bar"))
            # 更新开关状态
            self.lang_switch.setChecked(lang_code == "en")
            # 更新Tab标签
            self.update_tab_labels()
            # 更新所有子界面的语言
            self.update_all_tabs_language()

    def update_all_tabs_language(self):
        """更新所有Tab的语言"""
        for tab_key, tab_instance in self.tabs:
            if hasattr(tab_instance, 'update_language'):
                tab_instance.update_language()

if __name__ == "__main__":
    import sys
    print("正在启动 Twitch 关键词监控...")
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        print("界面已显示，请检查任务栏。")
        sys.exit(app.exec())
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
