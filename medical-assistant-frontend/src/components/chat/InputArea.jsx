import React, { useState } from "react";
import { Send, Wrench } from "lucide-react";
import Button from "../ui/Button";

const InputArea = ({ onSend, isLoading, onOpenTools }) => {
  const [query, setQuery] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSend(query);
      setQuery("");
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="border-t border-slate-200 bg-white p-4"
    >
      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a medical question..."
          className="medical-input flex-1"
          disabled={isLoading}
        />

        {onOpenTools && (
          <Button
            type="button"
            variant="secondary"
            onClick={onOpenTools}
            disabled={isLoading}
            title="Open Tools"
          >
            <Wrench className="w-5 h-5" />
          </Button>
        )}

        <Button
          type="submit"
          disabled={!query.trim() || isLoading}
          loading={isLoading}
        >
          <Send className="w-5 h-5" />
        </Button>
      </div>
      <p className="text-xs text-slate-500 mt-2">
        Press Enter to send • Shift+Enter for new line
      </p>
    </form>
  );
};

export default InputArea;
