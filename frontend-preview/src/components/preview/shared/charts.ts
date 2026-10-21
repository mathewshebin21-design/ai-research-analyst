import type { Projection, ScenarioKey, SensitivityRow } from "@/lib/finance";
import { eurK, MONTHS } from "@/lib/finance";
import { claims, competitors, factors, frameworks, sources, statusMeta, tasks, verdantPosition, type ClaimStatus } from "@/lib/sample-data";
import type { EChartOption } from "./echart";

export type Palette = {
  fg: string;
  muted: string;
  line: string;
  surface: string;
  accent: string;
  series: Record<ScenarioKey, string>;
  ok: string;
  warn: string;
  bad: string;
  font: string;
};

const months = Array.from({ length: MONTHS }, (_, i) => `M${i + 1}`);

function axisBase(p: Palette) {
  return {
    axisLine: { lineStyle: { color: p.line } },
    axisTick: { show: false },
    axisLabel: { color: p.muted, fontFamily: p.font, fontSize: 11 },
    splitLine: { lineStyle: { color: p.line, opacity: 0.6 } },
  };
}

function tooltip(p: Palette) {
  return {
    backgroundColor: p.surface,
    borderColor: p.line,
    textStyle: { color: p.fg, fontFamily: p.font, fontSize: 12 },
  };
}

export function cashOption(results: Record<ScenarioKey, Projection>, p: Palette, opts: { area?: boolean; labels?: boolean } = {}): EChartOption {
  const order: ScenarioKey[] = ["optimistic", "base", "conservative"];
  return {
    textStyle: { fontFamily: p.font },
    grid: { left: 52, right: opts.labels ? 92 : 16, top: 16, bottom: 28 },
    tooltip: { trigger: "axis", ...tooltip(p), valueFormatter: (v: number) => eurK(v) },
    xAxis: { type: "category", data: months, boundaryGap: false, ...axisBase(p), splitLine: { show: false }, axisLabel: { ...axisBase(p).axisLabel, interval: 5 } },
    yAxis: { type: "value", ...axisBase(p), axisLabel: { ...axisBase(p).axisLabel, formatter: (v: number) => eurK(v) } },
    series: order.map((key) => ({
      name: key === "base" ? "Base" : key === "optimistic" ? "Optimistic" : "Conservative",
      type: "line",
      showSymbol: false,
      smooth: false,
      data: results[key].cumulativeCash.map((v) => Math.round(v)),
      lineStyle: { width: key === "base" ? 2.5 : 1.5, color: p.series[key], type: key === "base" ? "solid" : "dashed" },
      itemStyle: { color: p.series[key] },
      areaStyle: opts.area && key === "base" ? { color: p.series.base, opacity: 0.08 } : undefined,
      endLabel: opts.labels
        ? { show: true, color: p.series[key], fontFamily: p.font, fontSize: 11, formatter: (s: { seriesName: string }) => s.seriesName }
        : undefined,
      markLine:
        key === "base"
          ? { symbol: "none", silent: true, label: { show: false }, lineStyle: { color: p.muted, type: "solid", width: 1 }, data: [{ yAxis: 0 }] }
          : undefined,
    })),
  };
}

export function tornadoOption(rows: SensitivityRow[], p: Palette): EChartOption {
  const data = [...rows].reverse();
  return {
    textStyle: { fontFamily: p.font },
    grid: { left: 112, right: 24, top: 28, bottom: 24 },
    legend: { top: 0, right: 0, itemWidth: 10, itemHeight: 10, textStyle: { color: p.muted, fontSize: 11 } },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, ...tooltip(p), valueFormatter: (v: number) => eurK(v) },
    xAxis: { type: "value", ...axisBase(p), axisLabel: { ...axisBase(p).axisLabel, formatter: (v: number) => eurK(v) } },
    yAxis: { type: "category", data: data.map((r) => r.label), ...axisBase(p), splitLine: { show: false } },
    series: [
      { name: "Input −20%", type: "bar", stack: "s", data: data.map((r) => Math.round(r.low)), itemStyle: { color: p.muted }, barWidth: 12 },
      { name: "Input +20%", type: "bar", stack: "s2", barGap: "-100%", data: data.map((r) => Math.round(r.high)), itemStyle: { color: p.accent }, barWidth: 12 },
    ],
  };
}

export function radarOption(p: Palette): EChartOption {
  return {
    textStyle: { fontFamily: p.font },
    tooltip: { ...tooltip(p) },
    radar: {
      radius: "58%",
      indicator: factors.map((f) => ({ name: f.short, max: 100 })),
      axisName: { color: p.muted, fontFamily: p.font, fontSize: 11 },
      splitLine: { lineStyle: { color: p.line } },
      splitArea: { show: false },
      axisLine: { lineStyle: { color: p.line } },
    },
    series: [
      {
        type: "radar",
        symbolSize: 4,
        data: [
          { name: "Score", value: factors.map((f) => f.score), lineStyle: { color: p.accent, width: 2 }, itemStyle: { color: p.accent }, areaStyle: { color: p.accent, opacity: 0.15 } },
          { name: "Evidence coverage", value: factors.map((f) => Math.round(f.coverage * 100)), lineStyle: { color: p.muted, type: "dashed" }, itemStyle: { color: p.muted } },
        ],
      },
    ],
  };
}

export function competitorOption(p: Palette): EChartOption {
  return {
    textStyle: { fontFamily: p.font },
    grid: { left: 44, right: 20, top: 16, bottom: 40 },
    tooltip: {
      ...tooltip(p),
      formatter: (x: { data: { name: string; value: number[]; range?: string } }) =>
        `${x.data.name}<br/>€${x.data.value[0]} · transparency ${x.data.value[1]}${x.data.range ? `<br/>share ${x.data.range}` : ""}`,
    },
    xAxis: { type: "value", name: "Core model price (€)", nameLocation: "middle", nameGap: 26, nameTextStyle: { color: p.muted, fontSize: 11 }, min: 130, max: 200, ...axisBase(p) },
    yAxis: { type: "value", name: "Transparency", nameTextStyle: { color: p.muted, fontSize: 11 }, min: 30, max: 100, ...axisBase(p) },
    series: [
      {
        type: "scatter",
        data: competitors.map((c) => ({ name: c.name, value: [c.price, c.transparency], range: `${c.shareLow}–${c.shareHigh}%`, symbolSize: 8 + (c.shareLow + c.shareHigh) * 0.9 })),
        itemStyle: { color: p.muted, opacity: 0.55, borderColor: p.fg, borderWidth: 0.5 },
        label: { show: true, position: "right", color: p.muted, fontSize: 10, formatter: (x: { name: string }) => x.name },
      },
      {
        type: "scatter",
        data: [{ name: verdantPosition.name, value: [verdantPosition.price, verdantPosition.transparency], symbolSize: 14 }],
        itemStyle: { color: p.accent },
        label: { show: true, position: "top", distance: 8, color: p.accent, fontSize: 11, fontWeight: 600, formatter: () => "Verdant (planned)" },
      },
    ],
  };
}

const statusOrder: ClaimStatus[] = ["supported", "partial", "contradicted", "unsupported", "missing"];

export function statusColor(p: Palette, s: ClaimStatus) {
  return { supported: p.ok, partial: p.warn, contradicted: p.bad, unsupported: p.bad, missing: p.muted }[s];
}

/** Claims per task by verification status. */
export function coverageHeatmap(p: Palette): EChartOption {
  const active = tasks.filter((t) => t.claims > 0);
  const data: [number, number, number][] = [];
  active.forEach((t, x) =>
    statusOrder.forEach((s, y) => data.push([x, y, claims.filter((c) => c.taskId === t.id && c.status === s).length])),
  );
  return {
    textStyle: { fontFamily: p.font },
    grid: { left: 92, right: 12, top: 8, bottom: 28 },
    tooltip: { ...tooltip(p), formatter: (x: { value: [number, number, number] }) => `${active[x.value[0]].id} · ${statusMeta[statusOrder[x.value[1]]].label}: ${x.value[2]}` },
    xAxis: { type: "category", data: active.map((t) => t.id), ...axisBase(p), splitLine: { show: false } },
    yAxis: { type: "category", data: statusOrder.map((s) => statusMeta[s].label.replace("Partially supported", "Partial")), ...axisBase(p), splitLine: { show: false } },
    visualMap: { show: false, min: 0, max: 2, inRange: { color: [p.surface, p.accent] } },
    series: [
      {
        type: "heatmap",
        data,
        label: { show: true, color: p.fg, fontFamily: p.font, fontSize: 11, formatter: (x: { value: number[] }) => (x.value[2] ? String(x.value[2]) : "") },
        itemStyle: { borderColor: p.line, borderWidth: 1 },
      },
    ],
  };
}

/** Claim ↔ source network; edge style encodes the verifier's relation. */
export function evidenceGraph(p: Palette, selected: string): EChartOption {
  const used = new Set(claims.flatMap((c) => c.evidence.map((e) => e.sourceId)));
  const nodes = [
    ...claims.map((c) => ({
      id: c.id,
      name: c.id,
      symbolSize: c.id === selected ? 26 : 18,
      itemStyle: { color: statusColor(p, c.status), borderColor: c.id === selected ? p.fg : "transparent", borderWidth: 2 },
      label: { show: true, color: p.fg, fontSize: 10, fontFamily: p.font },
    })),
    ...sources
      .filter((s) => used.has(s.id))
      .map((s) => ({
        id: s.id,
        name: s.id,
        symbol: "rect",
        symbolSize: 14,
        itemStyle: { color: p.surface, borderColor: p.muted, borderWidth: 1 },
        label: { show: true, color: p.muted, fontSize: 10, fontFamily: p.font },
      })),
  ];
  const links = claims.flatMap((c) =>
    c.evidence.map((e) => ({
      source: e.sourceId,
      target: c.id,
      lineStyle: {
        color: e.relation === "supports" ? p.ok : e.relation === "contradicts" ? p.bad : p.muted,
        type: e.relation === "related" ? "dashed" : "solid",
        width: c.id === selected ? 2.5 : 1,
        opacity: c.id === selected ? 1 : 0.5,
      },
    })),
  );
  return {
    tooltip: { show: false },
    series: [{ type: "graph", layout: "force", roam: false, draggable: false, force: { repulsion: 120, edgeLength: 46, gravity: 0.12 }, data: nodes, links }],
  };
}

export function porterOption(p: Palette): EChartOption {
  return {
    textStyle: { fontFamily: p.font },
    grid: { left: 96, right: 28, top: 4, bottom: 20 },
    xAxis: { type: "value", min: 0, max: 5, interval: 1, ...axisBase(p) },
    yAxis: { type: "category", data: frameworks.porter.map((f) => f.force).reverse(), ...axisBase(p), splitLine: { show: false } },
    series: [
      {
        type: "bar",
        data: frameworks.porter.map((f) => f.level).reverse(),
        barWidth: 10,
        itemStyle: { color: p.accent },
        label: { show: true, position: "right", color: p.muted, fontSize: 11, formatter: (x: { value: number }) => x.value.toFixed(1) },
      },
    ],
  };
}
