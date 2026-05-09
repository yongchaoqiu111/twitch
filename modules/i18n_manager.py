"""
国际化 (i18n) 管理模块
"""
import json
import os

class I18nManager:
    def __init__(self):
        # 获取 i18n 目录路径
        if getattr(__import__('sys'), 'frozen', False):
            self.i18n_dir = os.path.join(os.path.dirname(__import__('sys').executable), 'i18n')
        else:
            self.i18n_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'i18n')
        
        self.current_lang = 'zh'
        self.translations = {}
        self.load_language('zh')
    
    def load_language(self, lang_code):
        """加载指定语言文件"""
        lang_file = os.path.join(self.i18n_dir, f"{lang_code}.json")
        if os.path.exists(lang_file):
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
                self.current_lang = lang_code
                return True
            except Exception as e:
                print(f"加载语言文件失败: {e}")
                return False
        return False
    
    def t(self, key, **kwargs):
        """获取翻译文本"""
        text = self.translations.get(key, key)
        # 支持格式化：t('msg_hello', name='World')
        if kwargs:
            try:
                text = text.format(**kwargs)
            except:
                pass
        return text
    
    def set_language(self, lang_code):
        """切换语言"""
        return self.load_language(lang_code)
    
    def get_current_lang(self):
        """获取当前语言"""
        return self.current_lang
