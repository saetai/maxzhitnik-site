from playwright.sync_api import sync_playwright
import os

os.makedirs('review', exist_ok=True)
path = os.path.abspath('index.html')

with sync_playwright() as p:
    browser = p.chromium.launch()
    for w, label in [(1440,'desktop'), (390,'mobile')]:
        page = browser.new_page(viewport={'width':w,'height':900})
        page.goto(f'file://{path}')
        page.wait_for_timeout(2500)
        page.screenshot(path=f'review/full-{label}.png', full_page=True)
        print(f'full-{label}.png готов')
        # варианты hero
        for v in ['a','b']:
            page.goto(f'file://{path}?hero={v}')
            page.wait_for_timeout(1500)
            page.screenshot(path=f'review/hero-{v}-{label}.png', clip={'x':0,'y':0,'width':w,'height':900})
            print(f'hero-{v}-{label}.png готов')
    browser.close()
print('Скриншоты готовы в review/')
