import fs from "node:fs";
import path from "node:path";

import { marked } from "marked";

const DIR = path.join(process.cwd(), "content", "legal");

export const legalPages = {
  terms: "Terms of Service",
  privacy: "Privacy Notice",
  cookies: "Cookies and Local Storage",
  "acceptable-use": "Acceptable Use Policy",
  "ai-notice": "AI and Evidence Notice",
  subprocessors: "Subprocessors",
  dpa: "Data Processing Addendum",
} as const;

export type LegalSlug = keyof typeof legalPages;

export function company(): Record<string, string> {
  return JSON.parse(fs.readFileSync(path.join(DIR, "company.json"), "utf8"));
}

export function renderLegal(slug: LegalSlug): { html: string; unfilled: boolean } {
  const vars = company();
  const md = fs.readFileSync(path.join(DIR, `${slug}.md`), "utf8").replace(/\{\{(\w+)\}\}/g, (_, k) => vars[k] ?? `{{${k}}}`);
  const html = (marked.parse(md, { async: false }) as string).replace(/<table>/g, '<div class="table-wrap"><table>').replace(/<\/table>/g, "</table></div>");
  return { html, unfilled: /\[[A-Z][A-Z \-—]+\]/.test(md) };
}
