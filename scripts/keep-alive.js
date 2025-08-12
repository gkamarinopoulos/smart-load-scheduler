// scripts/keep-alive.js
const puppeteer = require("puppeteer");

(async () => {
  const url = process.env.APP_URL;
  if (!url) throw new Error("APP_URL not set");

  const browser = await puppeteer.launch({
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
    headless: "new",
  });
  const page = await browser.newPage();

  await page.setUserAgent(
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
  );

  // Φορτώνει πλήρως τη σελίδα (HTML/JS/CSS)
  await page.goto(url, { waitUntil: "networkidle2", timeout: 120000 });

  // Μικρή παραμονή για να θεωρηθεί πραγματική επίσκεψη
  await page.waitForTimeout(5000);

  await browser.close();
  console.log("Keep-alive OK:", url);
})();
