import { money } from "@/lib/format";
import type { RunDetail, ScenarioResults } from "@/lib/types";
import type { EChartOption } from "./echart";

const P = {
  fg: "#efe9dc",
  muted: "#a3a9b4",
  line: "rgba(239,233,220,0.13)",
  surface: "#0f1e35",
  accent: "#c8a65d",
  series: { base: "#c8a65d", optimistic: "#efe9dc", conservative: "#7d8aa0" },
  font: "Hanken Grotesk, system-ui, sans-serif",
};

const axis = {
  axisLine: { lineStyle: { color: P.line } },
  axisTick: { show: false },
  axisLabel: { color: P.muted, fontFamily: P.font, fontSize: 11 },
  splitLine: { lineStyle: { color: P.line, opacity: 0.6 } },
};
const tip = { backgroundColor: P.surface, borderColor: P.line, textStyle: { color: P.fg, fontFamily: P.font, fontSize: 12 } };

export function cashOption(r: ScenarioResults, sym = "£"): EChartOption {
  const order = ["optimistic", "base", "conservative"] as const;
  const names = { optimistic: "Optimistic", base: "Base", conservative: "Conservative" };
  return {
    textStyle: { fontFamily: P.font },
    grid: { left: 56, right: 96, top: 16, bottom: 28 },
    tooltip: { trigger: "axis", ...tip, valueFormatter: (v: number) => money(v, sym) },
    xAxis: { type: "category", boundaryGap: false, data: Array.from({ length: r.months }, (_, i) => `M${i + 1}`), ...axis, splitLine: { show: false }, axisLabel: { ...axis.axisLabel, interval: 5 } },
    yAxis: { type: "value", ...axis, axisLabel: { ...axis.axisLabel, formatter: (v: number) => money(v, sym) } },
    series: order.map((k) => ({
      name: names[k],
      type: "line",
      showSymbol: false,
      data: r.scenarios[k].cumulative_cash.map(Math.round),
      lineStyle: { width: k === "base" ? 2.5 : 1.5, color: P.series[k], type: k === "base" ? "solid" : "dashed" },
      itemStyle: { color: P.series[k] },
      endLabel: { show: true, color: P.series[k], fontSize: 11, formatter: () => names[k] },
      markLine: k === "base" ? { symbol: "none", silent: true, label: { show: false }, lineStyle: { color: P.muted, type: "solid", width: 1 }, data: [{ yAxis: 0 }] } : undefined,
    })),
  };
}

export function tornadoOption(r: ScenarioResults, sym = "£"): EChartOption {
  const rows = [...r.sensitivity].reverse();
  return {
    textStyle: { fontFamily: P.font },
    grid: { left: 150, right: 24, top: 28, bottom: 24 },
    legend: { top: 0, right: 0, itemWidth: 10, itemHeight: 10, textStyle: { color: P.muted, fontSize: 11 } },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, ...tip, valueFormatter: (v: number) => money(v, sym) },
    xAxis: { type: "value", ...axis, axisLabel: { ...axis.axisLabel, formatter: (v: number) => money(v, sym) } },
    yAxis: { type: "category", data: rows.map((x) => x.label), ...axis, splitLine: { show: false } },
    series: [
      { name: "Input −20%", type: "bar", stack: "a", data: rows.map((x) => Math.round(x.low)), itemStyle: { color: P.muted }, barWidth: 12 },
      { name: "Input +20%", type: "bar", stack: "b", barGap: "-100%", data: rows.map((x) => Math.round(x.high)), itemStyle: { color: P.accent }, barWidth: 12 },
    ],
  };
}

export function porterOption(run: RunDetail): EChartOption {
  const rows = [...run.porter].reverse();
  return {
    textStyle: { fontFamily: P.font },
    grid: { left: 100, right: 32, top: 4, bottom: 20 },
    xAxis: { type: "value", min: 0, max: 5, interval: 1, ...axis },
    yAxis: { type: "category", data: rows.map((f) => f.force), ...axis, splitLine: { show: false } },
    series: [{ type: "bar", data: rows.map((f) => f.level), barWidth: 10, itemStyle: { color: P.accent }, label: { show: true, position: "right", color: P.muted, fontSize: 11 } }],
  };
}
