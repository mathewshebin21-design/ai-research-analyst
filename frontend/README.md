# Web app

The Strategic Intelligence Hub product in design A (Executive Intelligence). Next.js 16, TypeScript, Tailwind 4, shadcn/ui-style components on Radix, Motion and ECharts. All figures come from the research API; the app holds no business logic.

```bash
cp .env.example .env.local   # point NEXT_PUBLIC_API_URL at the API
npm ci
npm run dev                  # http://localhost:3000
npm run typecheck && npm run lint
npm run e2e                  # starts the API with test doubles and runs the full journey in Chromium
```

| Route | Screen |
| --- | --- |
| `/` | Landing |
| `/sign-in`, `/accept-terms` | Sign-in and consent (version and time recorded by the API) |
| `/app` | Ask a question, upload PDFs, research history |
| `/app/run?id=…&view=dashboard\|research\|evidence` | Plan review, live progress, executive dashboard, research workspace, evidence inspector |
| `/app/compare?a=…&b=…` | Two runs side by side |
| `/app/account` | Export or delete your data |
| `/legal/<slug>` | Legal documents rendered from `content/legal/*.md` |

Legal documents live in `content/legal/`. Company details come from `content/legal/company.json`; pages show a draft warning until the placeholders are filled. See `content/legal/LAUNCH_CHECKLIST.md`.
