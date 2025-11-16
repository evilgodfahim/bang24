// fetch.js
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

(async () => {
  const url = "https://www.banglanews24.com/category/opinion";

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto(url, { waitUntil: "networkidle" });

  const html = await page.content();

  const dir = "saved";
  if (!fs.existsSync(dir)) fs.mkdirSync(dir);

  const filePath = path.join(dir, "opinion.html");
  fs.writeFileSync(filePath, html, "utf-8");

  await browser.close();

  // Regenerate index.html (always same name)
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
