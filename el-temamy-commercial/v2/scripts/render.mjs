// Usage: node render.mjs stills t1,t2,...   |   node render.mjs video out.mp4 fps
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { spawn } from 'child_process';
import path from 'path';
const [mode, a1, a2] = process.argv.slice(2);
const FFMPEG = process.env.FFMPEG;
const browser = await chromium.launch({ args: ['--font-render-hinting=none', '--disable-gpu-vsync'] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
page.on('console', m => console.log('[page]', m.text()));
page.on('pageerror', e => console.log('[pageerror]', e.message));
await page.goto('file://' + path.resolve((process.env.WEB || 'web') + '/index.html'));
await page.evaluate(() => window.ready);
const fontsOk = await page.evaluate(() => document.fonts.check('800 100px Cairo', 'صيدلية'));
console.log('Cairo loaded:', fontsOk);
if (mode === 'stills') {
  for (const t of a1.split(',').map(Number)) {
    await page.evaluate(t => window.renderAt(t), t);
    await page.screenshot({ path: `${process.env.STILLS || 'stills'}/t_${t.toFixed(2)}.png` });
  }
} else {
  const fps = Number(a2 || 30), N = Math.round(Number(process.env.DUR || 12) * fps);
  const ff = spawn(FFMPEG, ['-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-movflags', '+faststart', a1], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < N; i++) {
    await page.evaluate(t => window.renderAt(t), i / fps);
    const buf = await page.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 60 === 0) console.log('frame', i, '/', N);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
}
await browser.close();
