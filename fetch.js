const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

(async () => {
  const url = "https://www.banglanews24.com/category/opinion";

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    userAgent:
      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
  });

  await page.goto(url, {
    waitUntil: "domcontentloaded", // key change
    timeout: 60000,
  });

  // optional hard stop for late JS noise
  await page.waitForTimeout(2000);

  const html = await page.content();

  const dir = "saved";
  if (!fs.existsSync(dir)) fs.mkdirSync(dir);

  fs.writeFileSync(path.join(dir, "opinion.html"), html, "utf-8");

  await browser.close();

  const index = `
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Latest Opinion Snapshot</title>
<style>
body { font-family: sans-serif; margin: 40px; background: #fafafa; }
a { text-decoration: none; color: #0066cc; }
a:hover { text-decoration: underline; }
</style>
</head>
<body>
<h1>Latest Opinion Page Snapshot</h1>
<p><a href="saved/opinion.html">Click here to view the most recent saved page</a></p>
<p>This file overwrites itself every hour.</p>
</body>
</html>
  `;

  fs.writeFileSync("index.html", index.trim(), "utf-8");
})();