import type { Design, View } from "@/lib/use-hash-route";

export type Go = (design: Design | null, view?: View) => void;
export type PreviewProps = { view: View; go: Go };

export const navItems: { view: View; label: string; enabled: true }[] = [
  { view: "dashboard", label: "Executive dashboard", enabled: true },
  { view: "workspace", label: "Research workspace", enabled: true },
  { view: "evidence", label: "Evidence inspector", enabled: true },
];

/** Shown in navigation so the full information architecture is visible; built after approval. */
export const laterNav = ["Decision workspace", "Competitors", "Financial model", "Reports", "History"];
