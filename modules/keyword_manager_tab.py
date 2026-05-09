"""
关键词管理 Tab 界面 - 提供关键词的添加、删除、查看功能
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QGroupBox, QListWidget, QListWidgetItem,
                             QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from modules.keyword_manager import KeywordManager


class KeywordManagerTab(QWidget):
    def __init__(self, data_dir, i18n=None):
        super().__init__()
        self.data_dir = data_dir
        self.i18n = i18n
        self.keyword_manager = KeywordManager(data_dir)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        self.title_label = QLabel(self.i18n.t("keyword_title") if self.i18n else "关键词管理")
        self.title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # 关键词管理组
        self.keyword_group = QGroupBox(self.i18n.t("keyword_mgmt_group") if self.i18n else "关键词列表")
        keyword_layout = QVBoxLayout()
        
        # 添加关键词
        add_layout = QHBoxLayout()
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText(self.i18n.t("keyword_placeholder") if self.i18n else "输入关键词后点击添加")
        add_layout.addWidget(self.keyword_input)
        
        self.btn_add = QPushButton(self.i18n.t("btn_add") if self.i18n else "添加")
        self.btn_add.clicked.connect(self.add_keyword)
        add_layout.addWidget(self.btn_add)
        
        keyword_layout.addLayout(add_layout)
        
        # 关键词列表
        self.keyword_list = QListWidget()
        keyword_layout.addWidget(self.keyword_list)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        self.btn_delete = QPushButton(self.i18n.t("btn_delete_selected") if self.i18n else "删除选中")
        self.btn_delete.clicked.connect(self.delete_keyword)
        btn_layout.addWidget(self.btn_delete)
        
        self.btn_clear = QPushButton(self.i18n.t("btn_clear_all") if self.i18n else "清空全部")
        self.btn_clear.clicked.connect(self.clear_keywords)
        btn_layout.addWidget(self.btn_clear)
        
        keyword_layout.addLayout(btn_layout)
        self.keyword_group.setLayout(keyword_layout)
        layout.addWidget(self.keyword_group)
        
        # 消息显示
        self.message_label = QLabel("")
        self.message_label.setStyleSheet("color: green; padding: 10px;")
        layout.addWidget(self.message_label)
        
        layout.addStretch()
        
        # 加载关键词列表
        self.load_keywords()
    
    def update_language(self):
        """更新语言"""
        if not self.i18n:
            return
        self.title_label.setText(self.i18n.t("keyword_title"))
        self.keyword_group.setTitle(self.i18n.t("keyword_mgmt_group"))
        self.btn_add.setText(self.i18n.t("btn_add"))
        self.btn_delete.setText(self.i18n.t("btn_delete_selected"))
        self.btn_clear.setText(self.i18n.t("btn_clear_all"))
        self.keyword_input.setPlaceholderText(self.i18n.t("keyword_placeholder"))
    
    def load_keywords(self):
        """加载关键词列表"""
        self.keyword_list.clear()
        keywords = self.keyword_manager.get_keywords()
        for kw in keywords:
            item = QListWidgetItem(kw)
            self.keyword_list.addItem(item)
    
    def add_keyword(self):
        keyword = self.keyword_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "警告", "请输入关键词")
            return
        
        if self.keyword_manager.add_keyword(keyword):
            self.keyword_input.clear()
            self.load_keywords()
            self.show_message(f"关键词 '{keyword}' 已添加", "green")
        else:
            self.show_message(f"关键词 '{keyword}' 已存在", "orange")
    
    def delete_keyword(self):
        current_item = self.keyword_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要删除的关键词")
            return
        
        keyword = current_item.text()
        if self.keyword_manager.delete_keyword(keyword):
            self.load_keywords()
            self.show_message(f"关键词 '{keyword}' 已删除", "green")
    
    def clear_keywords(self):
        reply = QMessageBox.question(self, "确认", "确定要清空所有关键词吗？",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.keyword_manager.clear_keywords()
            self.load_keywords()
            self.show_message("所有关键词已清空", "green")
    
    def show_message(self, text, color):
        self.message_label.setText(text)
        self.message_label.setStyleSheet(f"color: {color}; padding: 10px;")
