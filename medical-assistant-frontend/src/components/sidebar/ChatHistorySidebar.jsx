import React, { useState, useEffect } from "react";
import { storage } from "../../lib/storage";
import { format } from "date-fns";
import { MessageSquare, Trash2, Search } from "lucide-react";
import Button from "../ui/Button";
import { showToast } from "../../lib/toast";

const ChatHistorySidebar = ({ onLoadChat, currentChatId }) => {
  const [chats, setChats] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    loadChats();
  }, []);

  const loadChats = () => {
    const savedChats = storage.getChats();
    setChats(savedChats);
  };

  const handleDeleteChat = (chatId, e) => {
    e.stopPropagation();

    if (window.confirm("Delete this conversation?")) {
      storage.deleteChat(chatId);
      loadChats();
      showToast.success("Conversation deleted");
    }
  };

  const handleClearAll = () => {
    if (
      window.confirm("Delete all conversation history? This cannot be undone.")
    ) {
      storage.clearAllChats();
      loadChats();
      showToast.success("All conversations cleared");
    }
  };

  const filteredChats = chats.filter(
    (chat) =>
      chat.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      chat.messages?.some((m) =>
        m.content?.toLowerCase().includes(searchQuery.toLowerCase()),
      ),
  );

  return (
    <div className="w-64 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-slate-200 dark:border-slate-700">
        <h2 className="font-bold text-slate-900 dark:text-white mb-3">
          Chat History
        </h2>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search chats..."
            className="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-slate-700 dark:text-white"
          />
        </div>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto">
        {filteredChats.length === 0 ? (
          <div className="p-4 text-center text-slate-500 dark:text-slate-400 text-sm">
            {searchQuery ? "No matching conversations" : "No chat history yet"}
          </div>
        ) : (
          <div className="p-2 space-y-1">
            {filteredChats.map((chat) => (
              <div
                key={chat.id}
                onClick={() => onLoadChat(chat)}
                className={`p-3 rounded-lg cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors group ${
                  currentChatId === chat.id
                    ? "bg-blue-50 dark:bg-blue-900/20"
                    : ""
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <MessageSquare className="w-4 h-4 text-blue-700 dark:text-blue-400 flex-shrink-0" />
                      <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                        {chat.title || "Untitled"}
                      </p>
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {format(new Date(chat.timestamp), "MMM d, h:mm a")}
                    </p>
                    <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
                      {chat.messages?.length || 0} messages
                    </p>
                  </div>

                  <button
                    onClick={(e) => handleDeleteChat(chat.id, e)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity text-slate-400 hover:text-red-600 dark:hover:text-red-400"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      {chats.length > 0 && (
        <div className="p-4 border-t border-slate-200 dark:border-slate-700">
          <Button
            variant="secondary"
            onClick={handleClearAll}
            className="w-full text-xs"
          >
            <Trash2 className="w-3 h-3 mr-2" />
            Clear All History
          </Button>
        </div>
      )}
    </div>
  );
};

export default ChatHistorySidebar;
