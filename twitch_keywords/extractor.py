import re

class KeywordExtractor:
    def __init__(self, keywords):
        # 将关键词转换为小写以便不区分大小写匹配
        self.keywords = [k.lower() for k in keywords]
        self.matches = []

    def process_message(self, user, message):
        """处理单条消息，检查是否包含关键词"""
        message_lower = message.lower()
        found_keywords = []
        
        for keyword in self.keywords:
            # 使用正则表达式确保匹配完整单词（可选，根据需求调整）
            if re.search(r'\b' + re.escape(keyword) + r'\b', message_lower):
                found_keywords.append(keyword)
        
        if found_keywords:
            result = {
                'user': user,
                'message': message,
                'matched_keywords': found_keywords
            }
            self.matches.append(result)
            return result
        return None

    def get_stats(self):
        """获取统计信息"""
        return {
            'total_matches': len(self.matches),
            'recent_matches': self.matches[-10:] # 返回最近10条
        }
