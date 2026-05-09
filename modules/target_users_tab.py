"""
目标用户筛选结果 Tab - 展示监控到的包含关键词的用户信息
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import csv
import os
from datetime import datetime


class TargetUsersTab(QWidget):
    def __init__(self, data_dir, i18n=None):
        super().__init__()
        self.data_dir = data_dir
        self.i18n = i18n
        self.csv_path = os.path.join(data_dir, "target_users.csv")
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        self.title_label = QLabel(self.i18n.t("target_users_title") if self.i18n else "目标用户筛选结果")
        self.title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton(self.i18n.t("btn_refresh_list") if self.i18n else "刷新列表")
        self.btn_refresh.clicked.connect(self.load_data)
        btn_layout.addWidget(self.btn_refresh)
        
        self.btn_clear = QPushButton(self.i18n.t("btn_clear_records") if self.i18n else "清空记录")
        self.btn_clear.clicked.connect(self.clear_data)
        btn_layout.addWidget(self.btn_clear)
        
        self.btn_deduplicate = QPushButton(self.i18n.t("btn_deduplicate") if self.i18n else "去重")
        self.btn_deduplicate.clicked.connect(self.deduplicate_data)
        btn_layout.addWidget(self.btn_deduplicate)
        
        self.btn_export = QPushButton(self.i18n.t("btn_export_text") if self.i18n else "导出到文本")
        self.btn_export.clicked.connect(self.export_to_text)
        btn_layout.addWidget(self.btn_export)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 数据表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            self.i18n.t("col_username") if self.i18n else "用户名",
            self.i18n.t("col_profile_url") if self.i18n else "主页链接",
            self.i18n.t("col_matched_keywords") if self.i18n else "匹配关键词",
            self.i18n.t("col_add_time") if self.i18n else "添加时间"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        
        # 初始加载数据
        self.load_data()
    
    def update_language(self):
        """更新语言"""
        if not self.i18n:
            return
        self.title_label.setText(self.i18n.t("target_users_title"))
        self.table.setHorizontalHeaderLabels([
            self.i18n.t("col_username"),
            self.i18n.t("col_profile_url"),
            self.i18n.t("col_matched_keywords"),
            self.i18n.t("col_add_time")
        ])
        self.btn_refresh.setText(self.i18n.t("btn_refresh_list"))
        self.btn_clear.setText(self.i18n.t("btn_clear_records"))
        self.btn_deduplicate.setText(self.i18n.t("btn_deduplicate"))
        self.btn_export.setText(self.i18n.t("btn_export_text"))
    
    def deduplicate_data(self):
        """按用户名去重，保留首次出现的记录"""
        if not os.path.exists(self.csv_path):
            QMessageBox.information(self, "提示", "暂无数据可去重")
            return
        
        try:
            # 读取所有数据
            rows = []
            with open(self.csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            # 去重（按用户名，保留首次出现）
            seen = set()
            unique_rows = []
            for row in rows:
                username = row.get('username', '')
                if username and username not in seen:
                    seen.add(username)
                    unique_rows.append(row)
            
            # 写回去重后的数据
            with open(self.csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=['username', 'profile_url', 'keywords', 'time'])
                writer.writeheader()
                writer.writerows(unique_rows)
            
            QMessageBox.information(self, "完成", f"去重完成！\n原记录数：{len(rows)}\n去重后：{len(unique_rows)}")
            self.load_data()  # 刷新界面
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"去重失败: {str(e)}")
    
    def export_to_text(self):
        """导出数据到文本文件"""
        if not os.path.exists(self.csv_path):
            QMessageBox.information(self, "提示", "暂无数据可导出")
            return
        
        # 选择保存位置
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出到文本文件", 
            os.path.join(self.data_dir, f"target_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"),
            "文本文件 (*.txt)"
        )
        
        if not file_path:
            return
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"总记录数：{len(rows)}\n")
                f.write("="*60 + "\n\n")
                
                for i, row in enumerate(rows, 1):
                    f.write(f"{i}. 用户名：{row.get('username', '')}\n")
                    f.write(f"   主页链接：{row.get('profile_url', '')}\n")
                    f.write(f"   匹配关键词：{row.get('keywords', '')}\n")
                    f.write(f"   添加时间：{row.get('time', '')}\n")
                    f.write("-"*60 + "\n")
            
            QMessageBox.information(self, "完成", f"导出成功！\n文件位置：{file_path}\n导出记录数：{len(rows)}")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"导出失败: {str(e)}")
    
    def load_data(self):
        """从 CSV 文件加载数据到表格"""
        self.table.setRowCount(0)
        
        if not os.path.exists(self.csv_path):
            return
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row_pos = self.table.rowCount()
                    self.table.insertRow(row_pos)
                    
                    self.table.setItem(row_pos, 0, QTableWidgetItem(row.get('username', '')))
                    
                    # 主页链接做成可点击的样式（简单展示）
                    url_item = QTableWidgetItem(row.get('profile_url', ''))
                    url_item.setForeground(Qt.GlobalColor.blue)
                    self.table.setItem(row_pos, 1, url_item)
                    
                    self.table.setItem(row_pos, 2, QTableWidgetItem(row.get('keywords', '')))
                    self.table.setItem(row_pos, 3, QTableWidgetItem(row.get('time', '')))
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载数据失败: {str(e)}")
    
    def clear_data(self):
        reply = QMessageBox.question(self, "确认", "确定要清空所有筛选出的用户记录吗？",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if os.path.exists(self.csv_path):
                os.remove(self.csv_path)
            self.load_data()
