import Link from "next/link";

const steps = [
  ["Plan", "Your question becomes a research plan you can edit before anything is searched."],
  ["Search", "Web sources and your own PDFs are collected and kept, with dates and page numbers."],
  ["Check", "Every claim is checked against an exact quote. Relevant is not the same as supported."],
  ["Decide", "Scores, scenarios and the verdict come from fixed rules you can inspect and change."],
];

export default function Home() {
  return (
    <div className="gutter mx-auto flex min-h-dvh max-w-[1100px] flex-col py-8">
      <header className="flex items-center justify-between gap-4">
        <p className="font-disp text-[20px]">Strategic Intelligence Hub</p>
        <Link href="/sign-in" className="border border-[var(--accent)] px-4 py-2 text-[13px] text-[var(--accent)] hover:bg-[var(--surface-2)]">
          Sign in
        </Link>
      </header>
      <section className="flex flex-1 flex-col justify-center gap-8 py-16">
        <p className="text-[11px] font-semibold tracking-[0.16em] text-[var(--accent)] uppercase">Market-entry research for decision makers</p>
        <h1 className="font-disp max-w-[20ch] text-[clamp(36px,5.5vw,64px)] leading-[1.05]">Board-ready answers, with every figure traced to its source.</h1>
        <p className="max-w-[60ch] text-[16px] leading-8 text-[var(--muted)]">
          Ask whether to enter a market. Get a plan, real sources, competitor and financial analysis, and a recommendation that says
          exactly what it rests on and what would change it.
        </p>
        <div className="flex flex-wrap gap-3">
          <Link href="/sign-in" className="bg-[var(--primary)] px-5 py-2.5 text-[14px] font-medium text-[var(--primary-fg)] hover:opacity-90">
            Start a question
          </Link>
          <Link href="/legal/ai-notice" className="border border-[var(--line)] px-5 py-2.5 text-[14px] hover:bg-[var(--surface-2)]">
            How the evidence works
          </Link>
        </div>
        <ol className="mt-6 grid gap-px border-y border-[var(--line)] bg-[var(--line)] sm:grid-cols-2 lg:grid-cols-4">
          {steps.map(([t, d]) => (
            <li key={t} className="bg-[var(--bg)] py-5 pr-5 sm:pl-5 sm:first:pl-0">
              <p className="font-disp text-[20px]">{t}</p>
              <p className="mt-1 text-[13.5px] leading-6 text-[var(--muted)]">{d}</p>
            </li>
          ))}
        </ol>
      </section>
      <footer className="flex flex-wrap gap-x-5 gap-y-2 border-t border-[var(--line)] pt-5 text-[12px] text-[var(--muted)]">
        <Link href="/legal/terms">Terms</Link>
        <Link href="/legal/privacy">Privacy</Link>
        <Link href="/legal/cookies">Cookies</Link>
        <Link href="/legal/acceptable-use">Acceptable use</Link>
        <Link href="/legal/ai-notice">AI notice</Link>
        <Link href="/legal/subprocessors">Subprocessors</Link>
        <span className="ml-auto">Not financial, investment or legal advice.</span>
      </footer>
    </div>
  );
}
