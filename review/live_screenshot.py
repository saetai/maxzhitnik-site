"""
Playwright скриншоты живого сайта https://saetai.github.io/maxzhitnik-site/
  - каждая секция отдельно (по id + hero)
  - ширины: 1440px и 390px
  - hero в вариантах ?hero=a и ?hero=b
  - результат: review/live/   и   review-live.zip
"""
import os, time, zipfile
from playwright.sync_api import sync_playwright

BASE = 'https://saetai.github.io/maxzhitnik-site/'
OUT  = os.path.join(os.path.dirname(__file__), 'live')
os.makedirs(OUT, exist_ok=True)

# Секции: (label, selector_для_прокрутки)
SECTIONS = [
    ('hero',      '.hero'),
    ('forwho',    '#forwho'),
    ('method',    '#method'),
    ('program',   '#program'),
    ('outcomes',  '#outcomes'),
    ('price',     '#price'),
    ('trainer',   '#trainer'),
    ('reviews',   '#reviews'),
]

WIDTHS = [
    (1440, 900,  'desktop'),
    (390,  844,  'mobile'),
]

def wait_loaded(page, timeout=8000):
    """Ждём шрифты + картинки, но не зависаем."""
    try:
        page.wait_for_load_state('networkidle', timeout=timeout)
    except Exception:
        pass
    page.wait_for_timeout(1500)

def scroll_to(page, selector):
    try:
        page.evaluate(
            f"document.querySelector('{selector}') && "
            f"document.querySelector('{selector}').scrollIntoView({{block:'start'}})"
        )
        page.wait_for_timeout(600)
    except Exception:
        pass

def screenshot_section(page, selector, path):
    try:
        el = page.query_selector(selector)
        if el:
            scroll_to(page, selector)
            el.screenshot(path=path)
            return True
    except Exception as e:
        print(f'  ⚠ {selector}: {e}')
    return False

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--disable-web-security'])

        for w, h, lbl in WIDTHS:
            print(f'\n── {lbl} ({w}×{h}) ──')
            page = browser.new_page(viewport={'width': w, 'height': h})
            # заранее грузим страницу с холодного старта
            page.goto(BASE, wait_until='domcontentloaded')
            wait_loaded(page)

            # 1) Полный скриншот
            full_path = os.path.join(OUT, f'full-{lbl}.png')
            page.screenshot(path=full_path, full_page=True)
            print(f'  ✓ full-{lbl}.png')

            # 2) Каждая секция
            for name, sel in SECTIONS:
                path = os.path.join(OUT, f'{name}-{lbl}.png')
                ok = screenshot_section(page, sel, path)
                print(f'  {"✓" if ok else "✗"} {name}-{lbl}.png')

            page.close()

            # 3) Hero A и B (отдельные загрузки)
            for v in ('a', 'b'):
                page2 = browser.new_page(viewport={'width': w, 'height': h})
                page2.goto(BASE + f'?hero={v}', wait_until='domcontentloaded')
                wait_loaded(page2)
                path = os.path.join(OUT, f'hero-{v}-{lbl}.png')
                ok = screenshot_section(page2, '.hero', path)
                print(f'  {"✓" if ok else "✗"} hero-{v}-{lbl}.png')
                page2.close()

        browser.close()

    # 4) Архив
    zip_path = os.path.join(os.path.dirname(__file__), '..', 'review-live.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fn in sorted(os.listdir(OUT)):
            if fn.endswith('.png'):
                zf.write(os.path.join(OUT, fn), os.path.join('review-live', fn))
    print(f'\n✅ Архив: {os.path.abspath(zip_path)}')
    print(f'✅ Скриншоты: {OUT}/')

if __name__ == '__main__':
    run()
