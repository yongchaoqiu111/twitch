"""
关键词管理模块 - 负责关键词的增删改查和持久化
"""
import json
import os


class KeywordManager:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.keyword_file = os.path.join(data_dir, "keywords.json")
        self.keywords = []
        self.load_keywords()
    
    def load_keywords(self):
        """从文件加载关键词"""
        if os.path.exists(self.keyword_file):
            try:
                with open(self.keyword_file, 'r', encoding='utf-8') as f:
                    self.keywords = json.load(f)
            except:
                self.keywords = []
        else:
            self.keywords = []
    
    def save_keywords(self):
        """保存关键词到文件"""
        with open(self.keyword_file, 'w', encoding='utf-8') as f:
            json.dump(self.keywords, f, ensure_ascii=False, indent=2)
    
    def add_keyword(self, keyword):
        """添加关键词，如果已存在则返回 False"""
        keyword = keyword.strip()
        if not keyword:
            return False
        
        if keyword in self.keywords:
            return False
        
        self.keywords.append(keyword)
        self.save_keywords()
        return True
    
    def delete_keyword(self, keyword):
        """删除关键词"""
        if keyword in self.keywords:
            self.keywords.remove(keyword)
            self.save_keywords()
            return True
        return False
    
    def clear_keywords(self):
        """清空所有关键词"""
        self.keywords = []
        self.save_keywords()
    
    def get_keywords(self):
        """获取所有关键词"""
        return self.keywords.copy()
