import React, { useState } from "react";

export function PromptInput({ onSend }: { onSend: (prompt: string) => Promise<void> }) {
  const [prompt, setPrompt] = useState("");

  return (
    <form
      className="border-t p-3 flex gap-2"
      onSubmit={async (e) => {
        e.preventDefault();
        if (!prompt.trim()) return;
        await onSend(prompt);
        setPrompt("");
      }}
    >
      <input
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Ask GraphMind to create or modify a chart..."
        className="flex-1 border rounded px-3 py-2"
      />
      <button type="submit" className="bg-slate-900 text-white px-4 py-2 rounded">
        Send
      </button>
    </form>
  );
}
