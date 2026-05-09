"""
测试：使用解析后的 Cookie 访问 Twitch 直播间
"""
from playwright.sync_api import sync_playwright
import json
import time

# 加载解析后的 Cookie
with open('twitch_cookie.json', 'r', encoding='utf-8') as f:
    cookies = json.load(f)

print(f"✅ 加载了 {len(cookies)} 个 Cookie")

with sync_playwright() as p:
    browser = p.chromium.launch(
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
    
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    )
    
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        window.chrome = { runtime: {} };
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
        Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
    """)
    
    # 添加 Cookie
    context.add_cookies(cookies)
    print("✅ 已注入 Cookie")
    
    page = context.new_page()
    
    # 访问目标直播间
    url = "https://www.twitch.tv/aya_chisu_"
    print(f"\n正在访问: {url}")
    
    try:
        page.goto(url, wait_until='domcontentloaded', timeout=120000)
        print("✅ 页面加载成功")
        
        # 等待页面完全加载（代理需要更长时间）
        print("等待页面完全加载（60秒）...")
        time.sleep(60)
        
        # 检查登录状态
        is_logged = page.evaluate("""
            () => {
                const loginBtn = document.querySelector('[data-a-target="login-button"]');
                const userMenu = document.querySelector('[data-a-target="user-menu"]');
                return !loginBtn || !!userMenu;
            }
        """)
        
        print("\n" + "="*60)
        if is_logged:
            print("✅ 登录成功！")
        else:
            print("❌ 未登录状态")
        print("="*60)
        
        # 提取聊天消息
        messages = page.evaluate("""
            () => {
                const result = [];
                const chatLines = document.querySelectorAll('[data-a-target="chat-line-message"]');
                
                chatLines.forEach((line) => {
                    try {
                        const userBadge = line.querySelector('[data-a-target="chat-badge"]');
                        const username = userBadge ? userBadge.getAttribute('alt') || userBadge.getAttribute('aria-label') : 'Unknown';
                        
                        const messageText = line.querySelector('[data-a-target="chat-message-text"]');
                        const message = messageText ? messageText.textContent.trim() : '';
                        
                        const timestamp = line.querySelector('[data-a-target="chat-timestamp"]');
                        const time = timestamp ? timestamp.textContent.trim() : '';
                        
                        if (message) {
                            result.push({ user: username, message, time });
                        }
                    } catch (e) {}
                });
                
                return result;
            }
        """)
        
        print(f"\n✅ 提取到 {len(messages)} 条聊天消息")
        if messages:
            print("\n前 5 条消息：")
            for i, msg in enumerate(messages[:5], 1):
                print(f"{i}. [{msg['time']}] {msg['user']}: {msg['message'][:60]}")
        
        input("\n按 Enter 关闭浏览器...")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        browser.close()
