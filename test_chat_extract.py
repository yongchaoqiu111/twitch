"""
直接测试聊天数据提取 - 按照用户提供的逻辑
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
    
    # 等待 60 秒让聊天完全加载
    print("等待页面完全加载（60秒）...")
    time.sleep(60)
    
    # =============================================
    # 核心：提取所有聊天消息（用户名 + 内容）
    # =============================================
    messages = page.query_selector_all(".chat-line__message")
    
    print(f"\n✅ 找到 {len(messages)} 条聊天消息\n")
    
    for i, msg in enumerate(messages[:20], 1):
        # 提取 data-a-user
        username = msg.get_attribute("data-a-user")
        
        # 提取聊天内容
        content_el = msg.query_selector(".text-fragment")
        content = content_el.inner_text() if content_el else ""
        
        print(f"{i}. 用户：{username}")
        print(f"   内容：{content}")
        print("-" * 30)
    
    input("\n按 Enter 关闭浏览器...")
    browser.close()
