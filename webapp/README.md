# വെബ് ඇප් (webapp)

සිම්පල් Node.js + Express දමලී ව්‍යාපෘතියක්. Static front-end එකක් සහ `/api/health` endpoint එකක් ඇත.

## ක්‍රියාත්මක කිරීම

1. Dependencies install කරන්න
   ```bash
   pnpm i
   ```
2. Dev server එක ධාවනය කරන්න
   ```bash
   pnpm dev
   ```
3. Browser එකෙන් යන්න: `http://localhost:3000`

## Deploy
- `pnpm start` දමලා production mode එකේ run කරගන්න.

## Directory structure
- `public/` — Static files (`index.html`)
- `server.js` — Express server
- `package.json` — Scripts සහ dependencies
