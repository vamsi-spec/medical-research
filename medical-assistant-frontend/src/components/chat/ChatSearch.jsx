import React, { useState } from "react";
import { Search, X } from "lucide-react";

const ChatSearch = ({ messages, onHighlight }) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [currentMatch, setCurrentMatch] = useState(0);
  const [totalMatches, setTotalMatches] = useState(0);

  const handleSearch = (query) => {
    setSearchQuery(query);

    if (!query.trim()) {
      setTotalMatches(0);
      setCurrentMatch(0);
      onHighlight(null);
      return;
    }

    // Find all matches
    const matches = [];
    messages.forEach((msg, msgIdx) => {
      const content = msg.type === "user" ? msg.content : msg.data.answer;
      const lowerContent = content.toLowerCase();
      const lowerQuery = query.toLowerCase();

      let index = lowerContent.indexOf(lowerQuery);
      while (index !== -1) {
        matches.push({ messageIndex: msgIdx, position: index });
        index = lowerContent.indexOf(lowerQuery, index + 1);
      }
    });

    setTotalMatches(matches.length);
    setCurrentMatch(matches.length > 0 ? 1 : 0);

    if (matches.length > 0) {
      onHighlight(matches[0]);
    }
  };

  const clearSearch = () => {
    setSearchQuery("");
    setTotalMatches(0);
    setCurrentMatch(0);
    onHighlight(null);
  };

  return (
    <div className="p-3 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800">
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="Search in conversation..."
            className="w-full pl-9 pr-20 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-slate-700 dark:text-white"
          />
          {searchQuery && (
            <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-2">
              <span className="text-xs text-slate-500">
                {totalMatches > 0
                  ? `${currentMatch}/${totalMatches}`
                  : "No matches"}
              </span>
              <button
                onClick={clearSearch}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatSearch;
