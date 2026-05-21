import React, { useState } from "react";
import { ChatPanel } from "./components/ChatPanel";
import { DatasetSidebar } from "./components/DatasetSidebar";
import { GraphCanvas } from "./components/GraphCanvas";
import { PromptInput } from "./components/PromptInput";
import { sendPrompt, uploadCsv } from "./services/api";

export default function App() {
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [datasets, setDatasets] = useState<Array<{ filename: string; columns: string[] }>>([]);
  const [figure, setFigure] = useState<any>(null);
  const [llmMode, setLlmMode] = useState<string>("unknown");

  return (
    <div className="h-screen bg-slate-100 p-4">
      <div className="h-full grid grid-cols-12 gap-4">
        <section className="col-span-4 bg-white rounded-lg border flex flex-col">
          <div className="p-3 border-b space-y-2">
            <input
              type="file"
              accept=".csv"
              multiple
              onChange={async (e) => {
                const files = Array.from(e.target.files || []);
                if (!files.length) return;
                const result = await uploadCsv(files);
                setDatasets(result.all_datasets);
              }}
            />
            <p className="text-xs text-slate-500">LLM mode: {llmMode}</p>
          </div>
          <div className="flex-1 min-h-0">
            <ChatPanel messages={messages} />
          </div>
          <DatasetSidebar datasets={datasets} />
          <PromptInput
            onSend={async (prompt) => {
              const result = await sendPrompt(prompt);
              setMessages(result.conversation_history);
              setFigure(result.figure);
              setDatasets(result.datasets);
              setLlmMode(result.llm_mode || "unknown");
            }}
          />
        </section>
        <section className="col-span-8">
          <GraphCanvas figure={figure} />
        </section>
      </div>
    </div>
  );
}
