const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  await p.goto('file://' + process.cwd() + '/index.html');
  await p.waitForTimeout(800);

  const r = await p.evaluate(() => {
    const q = s => {
      const el = document.querySelector(s);
      if (!el) return null;
      const rect = el.getBoundingClientRect();
      return { top: Math.round(rect.top), bottom: Math.round(rect.bottom),
               left: Math.round(rect.left), right: Math.round(rect.right),
               width: Math.round(rect.width), height: Math.round(rect.height) };
    };
    return {
      btn:  q('.btn-hero'),
      fig:  q('.hero-maxim-figure'),
      beam: q('.hero-beam-wrap'),
      line: q('.hero-beam-line'),
      glow: q('.hero-beam-glow'),
    };
  });

  console.log(JSON.stringify(r, null, 1));

  const btn  = r.btn,  fig  = r.fig,  beam = r.beam, line = r.line;
  const headEstimatedY = fig ? fig.top + 60 : null; // голова ~60px от верха фигуры

  const checks = [
    ['голова ниже кнопки на 150+',   fig && btn ? (fig.top + 60) - btn.bottom >= 150 : false],
    ['ширина фигуры 280–320px',      fig ? fig.width >= 280 && fig.width <= 320 : false],
    ['луч начинается не выше кнопки', beam && btn ? beam.top >= btn.bottom : false],
    ['линия не выше кнопки (или удалена)', !line || (btn ? line.top >= btn.bottom : true)],
    ['голова не выше кнопки',         fig  && btn ? (fig.top + 60) >= btn.bottom : false],
  ];

  console.log('\n--- checks ---');
  let allOk = true;
  checks.forEach(([name, ok]) => {
    console.log((ok ? 'OK   ' : 'FAIL ') + name);
    if (!ok) allOk = false;
  });
  console.log('\nbtn.bottom  =', btn?.bottom);
  console.log('fig.top     =', fig?.top, '  head_y =', headEstimatedY);
  console.log('beam.top    =', beam?.top);
  console.log('line.top    =', line?.top, '  line.bottom =', line ? line.top + line.height : null);

  await p.screenshot({ path: 'review/hero-1440.png' });
  await b.close();
  process.exit(allOk ? 0 : 1);
})();
