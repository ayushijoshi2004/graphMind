/**
 * GraphMind - AI-Powered Data Visualization
 *
 * Main application component that orchestrates the chat interface,
 * dataset management, and chart visualization.
 *
 * @component
 */

import React, { useState } from "react";
import { ChatPanel } from "./components/ChatPanel";
import { DatasetSidebar } from "./components/DatasetSidebar";
import { GraphCanvas } from "./components/GraphCanvas";
import { PromptInput } from "./components/PromptInput";
import { sendPrompt, uploadCsv } from "./services/api";

export default function App() {
    // Conversation history between user and AI
    const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);

    // Uploaded CSV datasets with their column information
    const [datasets, setDatasets] = useState<Array<{ filename: string; columns: string[] }>>([]);

    // Current chart figure data from Plotly
    const [figure, setFigure] = useState<any>(null);

    // LLM mode indicator (ollama/mock)
    const [llmMode, setLlmMode] = useState<string>("unknown");

    /**
     * Handle CSV file upload
     * Sends files to backend and updates dataset list
     */
    const handleFileUpload = async (files: FileList | null) => {
        const fileArray = Array.from(files || []);
        if (!fileArray.length) return;

        const result = await uploadCsv(fileArray);
        setDatasets(result.all_datasets);
    };

    /**
     * Handle chat message submission
     * Sends prompt to backend and updates UI with response
     */
    const handleSendMessage = async (prompt: string) => {
        const result = await sendPrompt(prompt);
        setMessages(result.conversation_history);
        setFigure(result.figure);
        setDatasets(result.datasets);
        setLlmMode(result.llm_mode || "unknown");
    };

    return (
        <div className="h-screen bg-[#FAFAFA] p-4">
            <div className="h-full grid grid-cols-12 gap-4">
                {/* Left Panel: Chat + Datasets */}
                <section className="col-span-4 bg-white rounded-xl border border-[#E5E5E5] flex flex-col overflow-hidden">
                    {/* Header with Logo and Upload */}
                    <div className="p-5 border-b border-[#F0F0F0]">
                        <div className="flex items-center justify-between mb-3">
                            <h2 className="text-base font-semibold text-[#171717]">GraphMind</h2>
                            <span className="text-xs text-[#737373] uppercase tracking-wide">
                {llmMode}
              </span>
                        </div>
                        <input
                            type="file"
                            accept=".csv"
                            multiple
                            onChange={(e) => handleFileUpload(e.target.files)}
                            className="hidden"
                            id="file-upload"
                        />
                        <label
                            htmlFor="file-upload"
                            className="block w-full px-4 py-2.5 bg-[#171717] text-white text-center rounded-lg text-sm font-medium cursor-pointer hover:bg-[#404040] transition-colors"
                        >
                            Upload CSV
                        </label>
                    </div>

                    {/* Chat Messages */}
                    <div className="flex-1 min-h-0">
                        <ChatPanel messages={messages} />
                    </div>

                    {/* Dataset List */}
                    <DatasetSidebar datasets={datasets} />

                    {/* Message Input */}
                    <PromptInput onSend={handleSendMessage} />
                </section>

                {/* Right Panel: Chart Visualization */}
                <section className="col-span-8">
                    <GraphCanvas figure={figure} />
                </section>
            </div>
        </div>
    );
}