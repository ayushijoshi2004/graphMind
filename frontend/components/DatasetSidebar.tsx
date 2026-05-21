import React from "react";

export function DatasetSidebar({ datasets }: { datasets: Array<{ filename: string; columns: string[] }> }) {
  return (
    <div className="border-t p-3 space-y-2">
      <h3 className="text-sm font-semibold text-slate-700">Uploaded datasets</h3>
      {datasets.map((dataset) => (
        <div key={dataset.filename} className="rounded border p-2 bg-slate-50">
          <div className="text-sm font-medium">{dataset.filename}</div>
          <div className="text-xs text-slate-500 truncate">{dataset.columns.join(", ")}</div>
        </div>
      ))}
    </div>
  );
}
