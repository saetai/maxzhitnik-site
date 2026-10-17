"""
Проходит по живому сайту и выводит все img/background-image с naturalWidth===0 (битые).
Должно быть 0 ошибок.
"""
from playwright.sync_api import sync_playwright

URL = 'https://saetai.github.io/maxzhitnik-site/'

JS_CHECK = """
() => {
  const broken = [];

  // 1) все <img>
  document.querySelectorAll('img').forEach(img => {
    if (!img.complete || img.naturalWidth === 0) {
      broken.push({ type: 'img', src: img.src || img.getAttribute('src'), alt: img.alt });
    }
  });

  // 2) background-image в inline style
  document.querySelectorAll('[style*="background-image"]').forEach(el => {
    const m = el.style.backgroundImage.match(/url\\(['"](.*?)['"]/);
    if (!m) return;
    const url = m[1];
    const tmp = new Image();
    tmp.src = url;
    // sync check не работает для bg — просто собираем URL для ручной проверки
    broken.push({ type: 'bg-inline', src: url, note: 'manual-check' });
  });

  return broken;
}
"""

JS_CHECK_NETWORK = """
async () => {
  // Пробуем загрузить все background-image через fetch
  const results = [];
  const els = document.querySelectorAll('[style*="background-image"]');
  for (const el of els) {
    const m = el.style.backgroundImage.match(/url\\(['"](.*?)['"]/);
    if (!m) continue;
    const url = m[1];
    try {
      const r = await fetch(url, { method: 'HEAD' });
      if (!r.ok) results.push({ type: 'bg', status: r.status, src: url });
    } catch(e) {
      results.push({ type: 'bg', status: 'error', src: url });
    }
  }
  return results;
}
"""

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1440, 'height': 900})

        errors = []

        def on_response(resp):
            if resp.request.resource_type in ('image',) and not resp.ok:
                errors.append({'type': 'network', 'status': resp.status, 'url': resp.url})

        page.on('response', on_response)

        print(f'Загружаем {URL} ...')
        page.goto(URL, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(2000)

        # Прокручиваем страницу чтобы все lazy-load картинки загрузились
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        page.wait_for_timeout(2000)
        page.evaluate('window.scrollTo(0, 0)')
        page.wait_for_timeout(1000)

        # Проверяем <img> через DOM
        broken_imgs = page.evaluate("""
        () => {
          const broken = [];
          document.querySelectorAll('img').forEach(img => {
            if (!img.complete || img.naturalWidth === 0) {
              broken.push({ src: img.getAttribute('src'), alt: img.alt || '' });
            }
          });
          return broken;
        }
        """)

        browser.close()

    print('\n─── Сетевые ошибки (статус ≠ 200) ───')
    if errors:
        for e in errors:
            print(f'  ✗ [{e["status"]}] {e["url"]}')
    else:
        print('  ✓ нет')

    print('\n─── Битые <img> (naturalWidth=0) ───')
    if broken_imgs:
        for b in broken_imgs:
            print(f'  ✗ src={b["src"]!r}  alt={b["alt"]!r}')
    else:
        print('  ✓ нет')

    total = len(errors) + len(broken_imgs)
    print(f'\n{"✅ ИТОГО: 0 ошибок" if total == 0 else f"❌ ИТОГО: {total} ошибок"}')

if __name__ == '__main__':
    run()
