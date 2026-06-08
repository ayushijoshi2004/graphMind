/**
 * ChatPanel Component
 *
 * Displays the conversation history between user and AI assistant.
 * Messages are styled differently based on sender role.
 *
 * @component
 */

import React from "react";

type Message = { role: string; content: string };

export function ChatPanel({ messages }: { messages: Message[] }) {
  return (
      <div className="h-full overflow-y-auto p-4 space-y-3">
        {messages.length === 0 ? (
            // Empty state when no messages
            <div className="h-full flex items-center justify-center text-center text-[#A3A3A3]">
              <div className="space-y-2">
                <div className="text-4xl">💬</div>
                <p className="text-sm">No messages yet</p>
                <p className="text-xs">Upload a CSV to get started</p>
              </div>
            </div>
        ) : (
            // Message list
            messages.map((m, idx) => (
                <div
                    key={idx}
                    className={`p-3 rounded-lg text-sm ${
                        m.role === "user"
                            ? "bg-[#F5F5F5] ml-5"
                            : "bg-white border border-[#E5E5E5] mr-5"
                    }`}
                >
            <span className="font-medium capitalize text-xs opacity-70 block mb-1">
              {m.role}:
            </span>
                  <span className="text-[#171717] leading-relaxed">{m.content}</span>
                </div>
            ))
        )}
      </div>
  );
}