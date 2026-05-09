"""
测试：注入 Cookie 后访问 Twitch 直播间并提取聊天消息
"""
from playwright.sync_api import sync_playwright
import json
import time

# 加载 Cookie
with open('twitch_cookie.json', 'r', encoding='utf-8') as f:
    cookies = json.load(f)

print(f"✅ 加载了 {len(cookies)} 个 Cookie")

with sync_playwright() as p:
    # 启动浏览器（最强过检测配置）
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
    
    # 创建上下文
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    )
    
    # 手动注入 JS 隐藏自动化特征
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        window.chrome = { runtime: {} };
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
        Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
    """)
    
    page = context.new_page()
    
    # 添加 Cookie
    context.add_cookies(cookies)
    print("✅ 已注入 Cookie")
    
    # 访问目标直播间（主页而不是 about）
    url = "https://www.twitch.tv/aya_chisu_"
    print(f"\n正在访问: {url}")
    
    try:
        page.goto(url, wait_until='domcontentloaded', timeout=60000)
        print("✅ 页面加载成功")
        
        # 等待聊天窗口加载
        time.sleep(10)
        
        # 尝试提取聊天消息
        messages = page.evaluate("""
            () => {
                const result = [];
                const chatLines = document.querySelectorAll('[data-a-target="chat-line-message"]');
                
                chatLines.forEach((line, index) => {
                    try {
                        // 提取用户名（从 chat-badge 或用户名容器）
                        const userBadge = line.querySelector('[data-a-target="chat-badge"]');
                        const username = userBadge ? userBadge.getAttribute('alt') || userBadge.getAttribute('aria-label') : 'Unknown';
                        
                        // 提取消息内容
                        const messageText = line.querySelector('[data-a-target="chat-message-text"]');
                        const message = messageText ? messageText.textContent.trim() : line.textContent.trim();
                        
                        // 提取时间戳
                        const timestamp = line.querySelector('[data-a-target="chat-timestamp"]');
                        const time = timestamp ? timestamp.textContent.trim() : '';
                        
                        if (message && message.length > 0) {
                            result.push({
                                user: username,
                                message: message,
                                time: time
                            });
                        }
                    } catch (e) {
                        console.error('Error parsing message:', e);
                    }
                });
                
                return result;
            }
        """)
        
        print(f"\n✅ 成功提取 {len(messages)} 条聊天消息")
        print("\n" + "="*60)
        
        # 显示前 10 条消息
        for i, msg in enumerate(messages[:10], 1):
            print(f"{i}. [{msg['time']}] {msg['user']}: {msg['message'][:80]}")
        
        print("="*60)
        print("\n如果看到消息列表，说明 Cookie 有效且能正常提取聊天内容")
        
        # 保持窗口打开
        input("\n按 Enter 键关闭浏览器...")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        browser.close()
