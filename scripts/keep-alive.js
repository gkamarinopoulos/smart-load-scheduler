// scripts/keep-alive.js
const puppeteer = require("puppeteer");
const URL = process.env.APP_URL || "https://smart-load-scheduler.onrender.com";

async function attempt(i) {
  const browser = await puppeteer.launch({
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
    headless: "new",
  });
  try {
    const page = await browser.newPage();
    await page.setUserAgent(
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    );
    page.setDefaultNavigationTimeout(180000);
    page.setDefaultTimeout(180000);

    const resp = await page.goto(URL, { waitUntil: "networkidle2", timeout: 180000 });
    const status = resp ? resp.status() : "no-response";
    console.log(`Attempt ${i}: HTTP ${status}`);
    await page.waitForTimeout(7000);

    await browser.close();
    return true;
  } catch (e) {
    console.error(`Attempt ${i} failed: ${e.message}`);
    await browser.close();
    return false;
  }
}

(async () => {
  for (let i = 1; i <= 3; i++) {
    if (await attempt(i)) {
      console.log("Keep-alive OK:", URL);
      process.exit(0);
    }
    await new Promise((r) => setTimeout(r, i * 5000));
  }
  console.error("All attempts failed");
  process.exit(1);
})();
