import Link from "next/link";
import { notFound } from "next/navigation";

import { legalPages, renderLegal, type LegalSlug } from "@/lib/legal";

export function generateStaticParams() {
  return Object.keys(legalPages).map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: PageProps<"/legal/[slug]">) {
  const { slug } = await params;
  return { title: `${legalPages[slug as LegalSlug] ?? "Legal"} · Strategic Intelligence Hub` };
}

export default async function LegalPage({ params }: PageProps<"/legal/[slug]">) {
  const { slug } = await params;
  if (!(slug in legalPages)) notFound();
  const { html, unfilled } = renderLegal(slug as LegalSlug);
  return (
    <div className="gutter mx-auto max-w-[760px] py-10">
      <nav aria-label="Legal" className="mb-8 flex flex-wrap gap-x-4 gap-y-2 text-[12.5px] text-[var(--muted)]">
        <Link href="/" className="text-[var(--fg)]">
          ← Strategic Intelligence Hub
        </Link>
        {Object.entries(legalPages).map(([s, title]) => (
          <Link key={s} href={`/legal/${s}`} aria-current={s === slug ? "page" : undefined} className={s === slug ? "text-[var(--accent)]" : "hover:text-[var(--fg)]"}>
            {title}
          </Link>
        ))}
      </nav>
      {unfilled && (
        <p role="note" className="mb-6 border-l-2 border-[var(--warn)] bg-[var(--warn-bg)] px-3 py-2 text-[13px] text-[var(--warn)]">
          Draft: company details in square brackets still need to be filled in before launch.
        </p>
      )}
      <article className="prose-legal" dangerouslySetInnerHTML={{ __html: html }} />
    </div>
  );
}
