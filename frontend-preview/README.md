# Design previews

Three working design directions for the Strategic Intelligence Hub, built with Next.js 16, TypeScript, Tailwind 4,
shadcn/ui-style components on Radix, Motion and ECharts.

**All data is illustrative.** It lives in `src/lib/sample-data.ts`, uses invented companies and `.example` source domains,
and every screen carries an "Illustrative data" marker. No API keys, no backend, no network calls.

## Run

```bash
npm ci
npm run dev          # http://localhost:3000
npm run build        # static export to out/
```

Routes are hash tokens so the static export works from any host:

| Hash | Screen |
| --- | --- |
| `#brief` (or none) | Review brief: audit, architecture, costs, milestones, design chooser |
| `#executive-dashboard`, `#executive-workspace`, `#executive-evidence` | A. Executive Intelligence |
| `#command-dashboard`, `#command-workspace`, `#command-evidence` | B. Intelligence Command |
| `#minimal-dashboard`, `#minimal-workspace`, `#minimal-evidence` | C. Minimal Intelligence |

## Layout

```
src/app/                    layout (fonts), page, theme tokens per [data-design]
src/components/ui/          shadcn/ui-style primitives (button, badge, tabs, slider, tooltip, …)
src/components/preview/     brief, router, and one folder per design direction
src/lib/sample-data.ts      illustrative research run
src/lib/finance.ts          deterministic scenario model (TypeScript mirror for the preview only)
```

The shadcn registry was unreachable from the build environment, so the primitives in `src/components/ui` were written by
hand on the same Radix + class-variance-authority pattern. `components.json` is in place so `npx shadcn add` works later.

## Hosted preview

`PREVIEW_RELATIVE_ASSETS=1 npm run build` emits `./_next/...` asset paths. `python scripts/artifact-page.py out dist-artifact`
then turns `out/index.html` into a body fragment for hosts that supply their own document skeleton, and moves assets to
`nx/` for hosts that reserve names starting with `_`. On such hosts React logs one
recoverable hydration warning (#418) because the host's `<head>` differs from the exported one; the page then renders
client-side and works normally.
