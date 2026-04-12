"""Take screenshots of all pages using Playwright."""
from playwright.sync_api import sync_playwright

BASE = "http://localhost:5173"
OUT = "."


def type_and_search(page, query):
    """Type query into input and click search - works with Vue v-model."""
    inp = page.locator(".search-bar input").first
    inp.click()
    inp.press("Control+a")
    inp.type(query, delay=20)
    page.wait_for_timeout(200)
    page.locator(".btn-search").first.click()
    page.wait_for_timeout(1200)


with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 900},
        device_scale_factor=2,
    )
    page = ctx.new_page()

    # 1. Boolean search
    page.goto(f"{BASE}/boolean")
    page.wait_for_timeout(300)
    type_and_search(page, "aerodynamics AND wing NOT flutter")
    page.screenshot(path=f"{OUT}/screenshot_boolean.png")
    print("1/5 boolean done")

    # 2. Phrase search
    page.goto(f"{BASE}/phrase")
    page.wait_for_timeout(300)
    type_and_search(page, "boundary layer")
    page.screenshot(path=f"{OUT}/screenshot_phrase.png")
    print("2/5 phrase done")

    # 3. Expanded search
    page.goto(f"{BASE}/expanded")
    page.wait_for_timeout(300)
    type_and_search(page, "heat transfer")
    page.screenshot(path=f"{OUT}/screenshot_expanded.png")
    print("3/5 expanded done")

    # 4. Index viewer with postings
    page.goto(f"{BASE}/index")
    page.wait_for_timeout(800)
    inp = page.locator(".search-bar input").first
    inp.click()
    inp.type("aero", delay=30)
    page.wait_for_timeout(200)
    page.locator(".btn-search").first.click()
    page.wait_for_timeout(600)
    # Click "查看倒排记录" for "aerodynam" (the one with DF=179)
    btns = page.locator(".btn-small")
    count = btns.count()
    for i in range(count):
        row = btns.nth(i).locator("xpath=ancestor::tr")
        text = row.inner_text()
        if "aerodynam" in text and "179" in text:
            btns.nth(i).click()
            break
    page.wait_for_timeout(600)
    page.screenshot(path=f"{OUT}/screenshot_index.png", full_page=True)
    print("4/5 index done")

    # 5. Boolean with detail expanded
    page.goto(f"{BASE}/boolean")
    page.wait_for_timeout(300)
    type_and_search(page, "aerodynamics AND wing")
    page.locator(".btn-detail").first.click()
    page.wait_for_timeout(600)
    page.screenshot(path=f"{OUT}/screenshot_detail.png")
    print("5/5 detail done")

    browser.close()
    print("All screenshots saved.")
