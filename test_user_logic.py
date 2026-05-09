"""
直接测试用户提供的提取逻辑
"""
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    url = "https://www.twitch.tv/na_na_san"
    print(f"正在访问: {url}")
    
    page.goto(url, wait_until='domcontentloaded', timeout=120000)
    print("✅ 页面加载成功")
    
    # 等待页面完全加载
    print("等待页面加载（60秒）...")
    time.sleep(60)
    
    # 用户提供的提取逻辑
    messages = page.query_selector_all(".chat-line__message")
    print(f"\n✅ 找到 {len(messages)} 条聊天消息")
    
    for i, msg in enumerate(messages[:5]):
        username = msg.get_attribute("data-a-user")
        content_elem = msg.query_selector(".text-fragment")
        content = content_elem.inner_text() if content_elem else ''
        
        print(f"\n用户：{username}")
        print(f"内容：{content}")
        print("-" * 30)
    
    input("\n按 Enter 关闭浏览器...")
    browser.close()
