import React, { useState, useEffect, useRef } from "react";
import { Toaster } from "react-hot-toast";
import Layout from "./components/layout/Layout";
import ChatContainer from "./components/chat/ChatContainer";
import InputArea from "./components/chat/InputArea";
import ChatSearch from "./components/chat/ChatSearch";
import ToolsMenu from "./components/tools/ToolsMenu";
import ChatHistorySidebar from "./components/sidebar/ChatHistorySidebar";
import BookmarksPanel from "./components/bookmarks/BookmarksPanel";
import DisclaimerModal from "./components/modals/DisclaimerModal";
import SettingsModal from "./components/modals/SettingsModal";
import ExportMenu from "./components/export/ExportMenu";
import KeyboardShortcutsHelp from "./components/help/KeyboardShortcutsHelp";
import useChatStore from "./store/chatStore";
import { medicalAPI } from "./api/endpoints";
import { storage } from "./lib/storage";
import { showToast } from "./lib/toast";
import { useKeyboardShortcuts } from "./hooks/useKeyboardShortcuts";
import {
  Settings,
  History,
  Bookmark,
  Download,
  HelpCircle,
} from "lucide-react";
import Button from "./components/ui/Button";

function App() {
  const {
    messages,
    isLoading,
    addMessage,
    setLoading,
    setError,
    clearMessages,
  } = useChatStore();

  // UI State
  const [showTools, setShowTools] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showBookmarks, setShowBookmarks] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  const [showDisclaimer, setShowDisclaimer] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showExport, setShowExport] = useState(false);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [currentChatId, setCurrentChatId] = useState(null);

  const inputRef = useRef(null);

  // Check disclaimer on mount
  useEffect(() => {
    const accepted = storage.hasAcceptedDisclaimer();
    if (!accepted) {
      setShowDisclaimer(true);
    }
  }, []);

  // Auto-save chat to history
  useEffect(() => {
    if (messages.length > 0) {
      const title =
        messages.find((m) => m.type === "user")?.content || "Untitled";
      storage.saveChat({
        id: currentChatId || Date.now(),
        title: title.substring(0, 50),
        messages,
      });
    }
  }, [messages, currentChatId]);

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onFocusSearch: () => {
      inputRef.current?.focus();
    },
    onNewChat: handleNewChat,
    onExport: () => {
      if (messages.length > 0) setShowExport(true);
    },
    onToggleBookmarks: () => setShowBookmarks(!showBookmarks),
    onToggleHistory: () => setShowHistory(!showHistory),
    onOpenSettings: () => setShowSettings(true),
    onEscape: () => {
      setShowSettings(false);
      setShowExport(false);
      setShowShortcuts(false);
    },
  });

  // Handle question mark key for shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.key === "?" && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        setShowShortcuts(true);
      }
    };
    window.addEventListener("keypress", handleKeyPress);
    return () => window.removeEventListener("keypress", handleKeyPress);
  }, []);

  const handleSendMessage = async (query) => {
    try {
      addMessage({
        type: "user",
        content: query,
      });

      setLoading(true);
      setError(null);

      const response = await medicalAPI.askQuestion(query);

      addMessage({
        type: "assistant",
        data: response,
        query: query, // Save query for bookmarks
      });
    } catch (error) {
      console.error("Error:", error);
      setError(error.message);

      addMessage({
        type: "assistant",
        data: {
          answer:
            "❌ Sorry, there was an error processing your request. Please make sure the backend API is running at http://localhost:8000 and try again.",
          citations: [],
          confidence: 0,
          refused: false,
        },
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    if (window.confirm("Clear all messages?")) {
      clearMessages();
      setCurrentChatId(null);
      showToast.success("Chat cleared");
    }
  };

  function handleNewChat() {
    if (messages.length > 0) {
      if (window.confirm("Start a new conversation?")) {
        clearMessages();
        setCurrentChatId(null);
        showToast.success("New chat started");
      }
    }
  }

  const handleLoadChat = (chat) => {
    clearMessages();
    chat.messages.forEach((msg) => addMessage(msg));
    setCurrentChatId(chat.id);
    setShowHistory(false);
    showToast.success("Chat loaded");
  };

  const handleAcceptDisclaimer = () => {
    storage.acceptDisclaimer();
    setShowDisclaimer(false);
    showToast.success("Welcome to Medical Research Assistant!");
  };

  const handleRating = (messageIndex, rating) => {
    console.log(`Message ${messageIndex} rated: ${rating}`);
    // You could save this to analytics/backend
  };

  return (
    <>
      <Layout onClearChat={messages.length > 0 ? handleClearChat : null}>
        <div className="h-full flex">
          {/* Chat History Sidebar */}
          {showHistory && (
            <ChatHistorySidebar
              onLoadChat={handleLoadChat}
              currentChatId={currentChatId}
            />
          )}

          {/* Main Chat Area */}
          <div className="flex-1 flex flex-col">
            {/* Top Action Bar */}
            <div className="border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2 flex items-center justify-between gap-2 no-print">
              <div className="flex items-center gap-2">
                <Button
                  variant="secondary"
                  onClick={() => setShowHistory(!showHistory)}
                  className="text-sm"
                  title="Chat History (Ctrl/Cmd + H)"
                >
                  <History className="w-4 h-4 sm:mr-2" />
                  <span className="hidden sm:inline">History</span>
                </Button>

                <Button
                  variant="secondary"
                  onClick={() => setShowBookmarks(!showBookmarks)}
                  className="text-sm"
                  title="Bookmarks (Ctrl/Cmd + B)"
                >
                  <Bookmark className="w-4 h-4 sm:mr-2" />
                  <span className="hidden sm:inline">Bookmarks</span>
                </Button>

                {messages.length > 0 && (
                  <Button
                    variant="secondary"
                    onClick={() => setShowExport(true)}
                    className="text-sm"
                    title="Export (Ctrl/Cmd + E)"
                  >
                    <Download className="w-4 h-4 sm:mr-2" />
                    <span className="hidden sm:inline">Export</span>
                  </Button>
                )}
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="secondary"
                  onClick={() => setShowShortcuts(true)}
                  className="text-sm"
                  title="Keyboard Shortcuts (?)"
                >
                  <HelpCircle className="w-4 h-4" />
                </Button>

                <Button
                  variant="secondary"
                  onClick={() => setShowSettings(true)}
                  className="text-sm"
                  title="Settings (Ctrl/Cmd + ,)"
                >
                  <Settings className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {/* Search Bar */}
            {showSearch && (
              <ChatSearch
                messages={messages}
                onHighlight={(match) => console.log("Highlight:", match)}
              />
            )}

            {/* Chat Messages */}
            <ChatContainer
              messages={messages}
              isLoading={isLoading}
              onRate={handleRating}
            />

            {/* Input Area */}
            <InputArea
              ref={inputRef}
              onSend={handleSendMessage}
              isLoading={isLoading}
              onOpenTools={() => setShowTools(!showTools)}
            />
          </div>

          {/* Tools Sidebar */}
          {showTools && (
            <div className="w-80 border-l border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
              <ToolsMenu />
            </div>
          )}

          {/* Bookmarks Panel */}
          {showBookmarks && (
            <div className="w-80 border-l border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 overflow-y-auto">
              <BookmarksPanel />
            </div>
          )}
        </div>
      </Layout>

      {/* Modals */}
      <DisclaimerModal
        isOpen={showDisclaimer}
        onAccept={handleAcceptDisclaimer}
      />

      <SettingsModal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
      />

      <ExportMenu
        isOpen={showExport}
        onClose={() => setShowExport(false)}
        messages={messages}
      />

      <KeyboardShortcutsHelp
        isOpen={showShortcuts}
        onClose={() => setShowShortcuts(false)}
      />

      {/* Toast Notifications */}
      <Toaster position="top-right" />
    </>
  );
}

export default App;
