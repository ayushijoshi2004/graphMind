/**
 * DatasetSidebar Component
 *
 * Displays list of uploaded CSV datasets with their column information.
 *
 * @component
 */

import React from "react";

export function DatasetSidebar({ datasets }: { datasets: Array<{ filename: string; columns: string[] }> }) {
    return (
        <div className="border-t border-[#F0F0F0] p-4 space-y-2 bg-[#FAFAFA]">
            <h3 className="text-xs font-semibold text-[#737373] uppercase tracking-wide mb-2">
                Uploaded Datasets {datasets.length > 0 && `(${datasets.length})`}
            </h3>

            {datasets.length === 0 ? (
                <div className="text-center py-4 text-xs text-[#A3A3A3]">
                    No datasets uploaded yet
                </div>
            ) : (
                datasets.map((dataset) => (
                    <div
                        key={dataset.filename}
                        className="bg-white border border-[#E5E5E5] rounded-md p-3"
                    >
                        <div className="text-sm font-medium text-[#171717] mb-1">
                            {dataset.filename}
                        </div>
                        <div className="text-xs text-[#737373]">
                            {dataset.columns.join(", ")}
                        </div>
                    </div>
                ))
            )}
        </div>
    );
}