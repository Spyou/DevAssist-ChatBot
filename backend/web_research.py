from playwright.async_api import async_playwright
from typing import List, Dict
import asyncio

class WebResearchService:
    def __init__(self):
        self.max_results = 5

    async def search_web(self, query: str) -> List[Dict[str, str]]:
        """Bing search using Playwright (visible browser, auto-wait, no manual ENTER required)"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)  # Show browser window
                context = await browser.new_context()
                page = await context.new_page()

                bing_url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
                print(f"🔍 Searching Bing: {bing_url}")
                await page.goto(bing_url, timeout=30000)
                await page.wait_for_timeout(7000)  # 7 seconds: adjust as needed for page/CAPTCHA

                results = []
                search_results = await page.query_selector_all('li.b_algo, .b_ans, .b_title')
                print(f"Bing: Found {len(search_results)} results")
                for idx, result in enumerate(search_results[:self.max_results*2]):
                    try:
                        link_elem = await result.query_selector('h2 a') or await result.query_selector('a')
                        title = await link_elem.inner_text() if link_elem else ""
                        url = await link_elem.get_attribute('href') if link_elem else ""
                        if not title or not url or not url.startswith('http'):
                            continue
                        snippet_elem = await result.query_selector('p') or link_elem
                        snippet = await snippet_elem.inner_text() if snippet_elem else ""
                        results.append({
                            'title': title.strip()[:200],
                            'url': url.strip(),
                            'snippet': snippet.strip()[:300]
                        })
                        if len(results) >= self.max_results:
                            break
                    except Exception as e:
                        print(f"⚠️ Error at result {idx}: {e}")
                        continue
                await browser.close()
                print(f"\n✅ Successfully extracted {len(results)} Bing results")
                return results
        except Exception as e:
            print(f"❌ Bing search error: {e}")
            import traceback
            traceback.print_exc()
            return []

    def is_programming_query(self, query: str) -> bool:
        programming_keywords = [
            'code', 'python', 'javascript', 'java', 'api', 'function',
            'error', 'debug', 'programming', 'algorithm', 'database',
            'sql', 'react', 'vue', 'django', 'fastapi', 'class', 'method',
            'syntax', 'compile', 'runtime', 'framework', 'library', 'rust',
            'go', 'typescript', 'flutter', 'dart', 'kotlin', 'swift',
            'c++', 'c#', 'php', 'ruby', 'html', 'css', 'nodejs', 'npm',
            'git', 'docker', 'kubernetes', 'aws', 'cloud', 'backend',
            'frontend', 'fullstack', 'async', 'websocket', 'rest', 'graphql',
            'tutorial', 'guide', 'documentation', 'example', 'how to', 'features',
            'latest', 'new', 'best', 'top'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in programming_keywords)

if __name__ == "__main__":
    async def test():
        ws = WebResearchService()
        results = await ws.search_web("latest dart version")
        print("\n" + "="*60)
        print(f"FINAL RESULTS: {len(results)} found")
        print("="*60 + "\n")
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['title']}")
            print(f"   URL: {r['url']}")
            print(f"   Snippet: {r['snippet'][:100]}...\n")
    asyncio.run(test())
