from playwright.async_api import async_playwright
from typing import Dict
import asyncio
from pathlib import Path
import re

class QwenService:
    def __init__(self):
        self.user_data_dir = Path(__file__).parent / "qwen_user_data"
        if not self.user_data_dir.exists():
            print("⚠️ Run 'python3 setup_qwen_login.py' first!")

    def clean_qwen_response(self, raw_text: str) -> str:
        """
        Clean Qwen response and add proper markdown formatting
        """

        # Remove UI noise
        noise_patterns = [
            r'Qwen\d+-\w+',
            r'\d+:\d+\s*[AP]M',
            r'Image\s+Edit',
            r'Web\s+Dev',
            r'Image\s+Generation',
            r'Video\s+Generation',
            r'Artifacts',
            r'Thinking',
            r'Search',
            r'AI-generated content may not be accurate\.',
            r'Copy\s+code',
            r'Copy',
            r'Regenerate',
            r'Stop\s+generating',
            r'Share'
        ]

        cleaned = raw_text
        for pattern in noise_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        languages = [
            'kotlin', 'dart', 'python', 'bash', 'javascript', 'java', 'rust', 'go',
            'cpp', 'sql', 'typescript', 'swift', 'ruby', 'php', 'html', 'css', 'json', 'c'
        ]

        lines = cleaned.split('\n')
        result_lines = []
        in_code_block = False
        code_block_lines = []
        current_lang = None

        for line in lines:
            stripped = line.strip()

            if stripped.isdigit():
                continue

            if stripped.lower() in languages and not in_code_block:
                current_lang = stripped.lower()
                in_code_block = True
                code_block_lines = []
                continue

            if in_code_block:
                if (not stripped or stripped.endswith(':')):
                    if code_block_lines:
                        result_lines.append(f'```{current_lang}')
                        result_lines.extend(code_block_lines)
                        result_lines.append('```')
                        result_lines.append('')
                    in_code_block = False
                    current_lang = None
                    code_block_lines = []
                    if stripped:
                        result_lines.append(line)
                else:
                    code_block_lines.append(line)
            else:
                if stripped:
                    result_lines.append(line)

        if in_code_block and code_block_lines:
            result_lines.append(f'```{current_lang}')
            result_lines.extend(code_block_lines)
            result_lines.append('```')

        cleaned = '\n'.join(result_lines)

        cleaned = re.sub(r'\n([A-Z][^:\n]{2,}:)\n', r'\n\n**\1**\n', cleaned)

        formatted_lines = []
        for line in cleaned.split('\n'):
            stripped = line.strip()
            if stripped and not stripped.startswith(('```', '-', '*', '1.')):
                formatted_lines.append(f'- {stripped}')
            else:
                formatted_lines.append(line)

        cleaned = '\n'.join(formatted_lines)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        return cleaned.strip()

    async def query_qwen(self, query: str) -> Dict[str, str]:
        """Query Qwen AI using your saved login session"""
        try:
            print("=" * 50)
            print("🤖 QWEN MODE ACTIVE")
            print(f"Query: {query}")
            print("=" * 50)

            async with async_playwright() as p:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(self.user_data_dir),
                    headless=False,
                    args=['--start-maximized'],
                    viewport={'width': 1920, 'height': 1080}
                )

                page = context.pages[0] if context.pages else await context.new_page()
                print("🤖 Opening Qwen...")
                await page.goto("https://chat.qwen.ai/", timeout=30000)
                await page.wait_for_timeout(5000)

                print("⏳ Sending query...")
                input_selectors = [
                    'textarea[placeholder*="Ask"]',
                    'textarea[placeholder*="message"]',
                    'textarea',
                    'div[contenteditable="true"]'
                ]

                input_sent = False
                for selector in input_selectors:
                    try:
                        inp = await page.query_selector(selector)
                        if inp:
                            await inp.click()
                            await page.wait_for_timeout(300)
                            await inp.fill(query)
                            await page.keyboard.press('Enter')
                            input_sent = True
                            print("✅ Query sent")
                            break
                    except:
                        continue

                if not input_sent:
                    await context.close()
                    return {"title": "Qwen Error", "content": "⚠️ Could not find input field"}

                await page.wait_for_timeout(25000)

                print("🔍 Extracting response...")
                qwen_answer = await page.evaluate('''
                    () => {
                        const selectors = [
                            '.prose',
                            '.markdown-body',
                            '[class*="message-content"]',
                            '[class*="MessageContent"]',
                            '[class*="answer"]'
                        ];
                        for (let sel of selectors) {
                            const els = document.querySelectorAll(sel);
                            if (els.length > 0) {
                                return els[els.length - 1].innerText;
                            }
                        }
                        return null;
                    }
                ''')

                if qwen_answer:
                    content = self.clean_qwen_response(qwen_answer)
                    await context.close()
                    return {"title": "🤖 Qwen AI Response", "content": content}

                screenshot = Path(__file__).parent / "qwen_debug.png"
                await page.screenshot(path=str(screenshot), full_page=True)
                await context.close()
                return {"title": "Qwen Error", "content": "⚠️ Debug screenshot saved"}

        except Exception as e:
            return {"title": "Qwen Error", "content": f"Failed: {str(e)}"}
