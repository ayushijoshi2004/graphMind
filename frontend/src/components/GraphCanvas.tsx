import React from "react";
const Plot = React.lazy(() => import("react-plotly.js"));

export function GraphCanvas({ figure }: { figure: any }) {
  return (
    <div className="h-full w-full bg-white rounded-lg border p-3">
      {figure ? (
        <React.Suspense fallback={<p>Loading chart renderer…</p>}>
        <Plot data={figure.data} layout={{ ...figure.layout, autosize: true }} style={{ width: "100%", height: "100%" }} />
        </React.Suspense>
      ) : (
        <div className="h-full flex items-center justify-center text-slate-400">No chart yet.</div>
      )}
    </div>
  );
}
