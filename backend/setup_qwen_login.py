from playwright.sync_api import sync_playwright
from pathlib import Path
import time

# This script runs ONCE to save your Qwen login
user_data_dir = Path(__file__).parent / "qwen_user_data"
user_data_dir.mkdir(exist_ok=True)

print("=" * 60)
print("🤖 QWEN LOGIN SETUP")
print("=" * 60)
print("\n1. Browser will open")
print("2. Login to your Qwen account manually")
print("3. After login, wait on the chat page for 10 seconds")
print("4. Script will save your session automatically\n")

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(user_data_dir),
        headless=False,
        args=['--start-maximized'],
        viewport={'width': 1920, 'height': 1080}
    )
    
    page = context.pages[0] if context.pages else context.new_page()
    
    print("🌐 Opening Qwen...")
    page.goto("https://chat.qwen.ai/", timeout=30000)
    
    print("\n⏳ Please login manually in the browser window...")
    print("⏳ After login, stay on the chat page for 10 seconds...")
    
    # Wait for user to login
    time.sleep(60)  # 60 seconds to login
    
    print("\n✅ Login session saved!")
    print("✅ Close the browser. You won't need to login again.")
    
    context.close()

print("\n" + "=" * 60)
print("✅ Setup complete! Now use Qwen in your chatbot.")
print("=" * 60)
