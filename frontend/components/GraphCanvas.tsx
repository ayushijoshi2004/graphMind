/**
 * GraphCanvas Component
 *
 * Renders interactive Plotly charts or displays an empty state.
 *
 * @component
 */

import React from "react";
import Plot from "react-plotly.js";

export function GraphCanvas({ figure }: { figure: any }) {
  return (
      <div className="h-full w-full bg-white rounded-xl border border-[#E5E5E5] p-6">
        {figure ? (
            <Plot
                data={figure.data}
                layout={{
                  ...figure.layout,
                  autosize: true,
                  paper_bgcolor: 'rgba(0,0,0,0)',
                  plot_bgcolor: 'rgba(0,0,0,0)',
                  font: {
                    family: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
                    color: '#171717',
                  },
                }}
                config={{
                  responsive: true,
                  displayModeBar: true,
                  displaylogo: false,
                }}
                style={{ width: "100%", height: "100%" }}
                useResizeHandler={true}
            />
        ) : (
            <div className="h-full flex items-center justify-center text-center">
              <div className="space-y-3">
                <div className="text-5xl">📊</div>
                <p className="text-sm font-medium text-[#171717]">No chart yet</p>
                <p className="text-xs text-[#A3A3A3]">Upload a CSV and ask a question</p>
              </div>
            </div>
        )}
      </div>
  );
}