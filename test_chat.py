"""
直接打开页面测试聊天数据抓取
"""
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        channel='chrome',
        args=['--start-maximized']
    )
    
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
    
    url = "https://www.twitch.tv/aya_chisu_"
    print(f"正在访问: {url}")
    
    page.goto(url, wait_until='domcontentloaded', timeout=120000)
    print("✅ 页面加载成功")
    
    # 等待 60 秒
    print("等待页面完全加载（60秒）...")
    time.sleep(60)
    
    # 调试：查找聊天容器
    print("\n正在查找聊天容器...")
    chat_container_found = page.evaluate("""
        () => {
            const selectors = [
                '[data-a-target="chat-list"]',
                '.chat-list',
                '[data-test-selector="chat-room-component-layout"]',
                '#root [class*="chat-list"]',
                '[role="log"]'
            ];
            
            for (const selector of selectors) {
                const el = document.querySelector(selector);
                if (el) {
                    console.log('找到:', selector);
                    return selector;
                }
            }
            return null;
        }
    """)
    
    if chat_container_found:
        print(f"✅ 找到聊天容器: {chat_container_found}")
    else:
        print("❌ 未找到聊天容器")
    
    # 调试：查看第一条聊天消息的DOM结构
    print("\n正在分析DOM结构...")
    dom_structure = page.evaluate("""
        () => {
            const chatLines = document.querySelectorAll('[data-a-target="chat-line-message"]');
            if (chatLines.length === 0) return '未找到聊天行';
            
            const firstLine = chatLines[0];
            
            // 获取完整的DOM层级
            let current = firstLine;
            const hierarchy = [];
            
            for (let i = 0; i < 5 && current; i++) {
                hierarchy.push({
                    level: i,
                    tag: current.tagName,
                    class: current.className?.substring(0, 50),
                    'data-a-user': current.getAttribute('data-a-user'),
                    'data-a-target': current.getAttribute('data-a-target'),
                    html: current.outerHTML.substring(0, 200)
                });
                current = current.parentElement;
            }
            
            return hierarchy;
        }
    """)
    
    print("\nDOM层级结构:")
    import json
    print(json.dumps(dom_structure, ensure_ascii=False, indent=2))
    
    # 提取聊天消息
    messages = page.evaluate("""
        () => {
            const result = [];
            const chatLines = document.querySelectorAll('[data-a-target="chat-line-message"]');
            
            console.log('找到聊天行:', chatLines.length);
            
            chatLines.forEach((line, index) => {
                try {
                    // 用户名从父级或祖父级获取
                    const level0 = line.getAttribute('data-a-user');
                    const level1 = line.parentElement?.getAttribute('data-a-user');
                    const level2 = line.parentElement?.parentElement?.getAttribute('data-a-user');
                    
                    const username = level2 || level1 || level0 || 'Unknown';
                    
                    // 消息内容选择器
                    const messageText = line.querySelector('[data-a-target="chat-message-text"]');
                    const message = messageText ? messageText.textContent.trim() : '';
                    
                    // 时间戳选择器
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
        print("\n前 10 条消息：")
        for i, msg in enumerate(messages[:10], 1):
            print(f"{i}. [{msg['time']}] {msg['user']}: {msg['message'][:80]}")
    else:
        print("\n❌ 未提取到消息")
    
    input("\n按 Enter 关闭浏览器...")
    browser.close()
