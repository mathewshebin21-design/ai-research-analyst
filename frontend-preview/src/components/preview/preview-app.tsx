"use client";

import { useEffect } from "react";
import { AnimatePresence, MotionConfig } from "motion/react";

import { TooltipProvider } from "@/components/ui/tooltip";
import { useHashRoute } from "@/lib/use-hash-route";
import { Brief } from "./brief";
import { CommandPreview } from "./command/command-preview";
import { ExecutivePreview } from "./executive/executive-preview";
import { MinimalPreview } from "./minimal/minimal-preview";
import { PreviewSwitcher } from "./shared/preview-switcher";

export function PreviewApp() {
  const { route, go } = useHashRoute();
  const { design, view } = route;

  useEffect(() => {
    document.documentElement.dataset.design = design ?? "";
    document.title = design ? `${design[0].toUpperCase()}${design.slice(1)} · Strategic Intelligence Hub` : "Strategic Intelligence Hub";
  }, [design]);

  return (
    <MotionConfig reducedMotion="user">
      <TooltipProvider>
        {design === null && <Brief go={go} />}
        {design !== null && (
          <div data-design={design}>
            <AnimatePresence initial={false} mode="wait">
              {design === "executive" && <ExecutivePreview key="executive" view={view} go={go} />}
              {design === "command" && <CommandPreview key="command" view={view} go={go} />}
              {design === "minimal" && <MinimalPreview key="minimal" view={view} go={go} />}
            </AnimatePresence>
            <PreviewSwitcher design={design} view={view} go={go} />
          </div>
        )}
      </TooltipProvider>
    </MotionConfig>
  );
}
