"""
Cookie 解析工具 - 将浏览器复制的文本格式转换为 Playwright 可用的 JSON 格式
"""
import json
from datetime import datetime


def parse_cookie_text(text_file, output_file):
    """
    解析浏览器复制的 Cookie 文本
    
    格式：Name\tValue\tDomain\tPath\tExpires\tSize\tHttpOnly\tSecure\tSameSite\t...
    """
    with open(text_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cookies = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split('\t')
        if len(parts) < 3:
            continue
        
        # 解析各字段（严格按照浏览器复制的列顺序）
        name = parts[0]
        value = parts[1]
        domain = parts[2]
        path = parts[3]
        expires_str = parts[4]
        
        # 浏览器复制的列顺序：Name, Value, Domain, Path, Expires, Size, HttpOnly, Secure, SameSite, ...
        # HttpOnly 在第 7 列 (索引 6), Secure 在第 8 列 (索引 7), SameSite 在第 9 列 (索引 8)
        http_only = False
        secure = False
        same_site = "None"
        
        # 解析 HttpOnly (索引 6)
        if len(parts) > 6 and parts[6].strip() == '✓':
            http_only = True
        
        # 解析 Secure (索引 7)
        if len(parts) > 7 and parts[7].strip() == '✓':
            secure = True
        
        # 解析 SameSite (索引 8)
        if len(parts) > 8:
            same_site_val = parts[8].strip()
            if same_site_val in ['None', 'Lax', 'Strict']:
                same_site = same_site_val
        
        # 解析过期时间
        expires = None
        if expires_str and expires_str != 'Session':
            try:
                # 解析 ISO 8601 格式: 2027-05-08T09:06:43.658Z
                dt = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
                expires = dt.timestamp()
            except:
                try:
                    # 尝试其他格式
                    dt = datetime.strptime(expires_str, '%Y-%m-%d %H:%M:%S')
                    expires = dt.timestamp()
                except:
                    pass
        
        cookie = {
            'name': name,
            'value': value,
            'domain': domain,
            'path': path,
            'httpOnly': http_only,
            'secure': secure,
            'sameSite': same_site
        }
        
        if expires:
            cookie['expires'] = expires
        
        cookies.append(cookie)
    
    # 保存到 JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 成功解析 {len(cookies)} 个 Cookie")
    print(f"✅ 已保存到: {output_file}")
    
    return cookies


if __name__ == '__main__':
    import os
    
    # 默认路径
    cookie_txt = 'cookie.txt'
    cookie_json = 'twitch_cookie.json'
    
    if os.path.exists(cookie_txt):
        parse_cookie_text(cookie_txt, cookie_json)
    else:
        print(f" 找不到 {cookie_txt} 文件")
        print("请将浏览器复制的 Cookie 保存为 cookie.txt 放在当前目录")
