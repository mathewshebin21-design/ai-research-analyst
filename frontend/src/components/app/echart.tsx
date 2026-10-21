"use client";

import { useEffect, useRef } from "react";
import * as echarts from "echarts/core";
import { BarChart, GraphChart, HeatmapChart, LineChart, RadarChart, ScatterChart } from "echarts/charts";
import {
  GridComponent,
  LegendComponent,
  MarkLineComponent,
  MarkAreaComponent,
  RadarComponent,
  TooltipComponent,
  VisualMapComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([
  LineChart,
  BarChart,
  ScatterChart,
  RadarChart,
  HeatmapChart,
  GraphChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  MarkLineComponent,
  MarkAreaComponent,
  RadarComponent,
  VisualMapComponent,
  CanvasRenderer,
]);

export type EChartOption = echarts.EChartsCoreOption;

export function EChart({
  option,
  className,
  label,
  onClick,
}: {
  option: EChartOption;
  className?: string;
  label: string;
  onClick?: (params: { name?: string; dataIndex?: number; data?: unknown }) => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const chart = useRef<echarts.ECharts | null>(null);
  const clickRef = useRef(onClick);

  useEffect(() => {
    clickRef.current = onClick;
  });

  useEffect(() => {
    if (!ref.current) return;
    const instance = echarts.init(ref.current, undefined, { renderer: "canvas" });
    chart.current = instance;
    instance.on("click", (p) => clickRef.current?.(p as never));
    const ro = new ResizeObserver(() => instance.resize());
    ro.observe(ref.current);
    return () => {
      ro.disconnect();
      instance.dispose();
      chart.current = null;
    };
  }, []);

  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    chart.current?.setOption({ animation: !reduce, ...option }, { notMerge: true });
  }, [option]);

  return <div ref={ref} role="img" aria-label={label} className={className} />;
}
