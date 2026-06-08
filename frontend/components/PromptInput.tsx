/**
 * PromptInput Component
 *
 * Text input form for submitting chat messages to the AI.
 *
 * @component
 */

import React, { useState } from "react";

export function PromptInput({ onSend }: { onSend: (prompt: string) => Promise<void> }) {
    const [prompt, setPrompt] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!prompt.trim() || isSubmitting) return;

        setIsSubmitting(true);
        try {
            await onSend(prompt);
            setPrompt("");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <form
            className="border-t border-[#F0F0F0] p-4 bg-white"
            onSubmit={handleSubmit}
        >
            <div className="flex gap-2">
                <input
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Ask a question..."
                    disabled={isSubmitting}
                    className="flex-1 px-3 py-2 border border-[#E5E5E5] rounded-lg text-sm focus:outline-none focus:border-[#171717] disabled:bg-[#F5F5F5] disabled:cursor-not-allowed"
                />
                <button
                    type="submit"
                    disabled={!prompt.trim() || isSubmitting}
                    className="px-5 py-2 bg-[#171717] text-white rounded-lg text-sm font-medium hover:bg-[#404040] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    {isSubmitting ? "Sending..." : "Send"}
                </button>
            </div>
        </form>
    );
}