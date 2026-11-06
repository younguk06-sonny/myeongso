// 공공데이터포털 '전국주차장정보표준데이터' 엑셀 파일 받기 (GitHub Actions에서 실행)
import { chromium } from 'playwright';
const out = process.argv[2] || 'parking-src.xls';
const browser = await chromium.launch();
const page = await (await browser.newContext({ acceptDownloads: true })).newPage();
await page.goto('https://www.data.go.kr/data/15012896/standard.do', { waitUntil: 'networkidle', timeout: 90000 });
const [dl] = await Promise.all([
  page.waitForEvent('download', { timeout: 300000 }),
  page.click('#stdXlsDownloadBtn', { timeout: 20000 })
]);
await dl.saveAs(out);
console.log('saved', out, dl.suggestedFilename());
await browser.close();
