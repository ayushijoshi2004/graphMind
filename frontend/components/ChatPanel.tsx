import React from "react";

type Message = { role: string; content: string };

export function ChatPanel({ messages }: { messages: Message[] }) {
  return (
    <div className="h-full overflow-y-auto p-4 space-y-3">
      {messages.map((m, idx) => (
        <div key={idx} className={m.role === "user" ? "text-slate-800" : "text-slate-500"}>
          <span className="font-medium capitalize mr-2">{m.role}:</span>
          <span>{m.content}</span>
        </div>
      ))}
    </div>
  );
}
