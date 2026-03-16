import React, { useState } from "react";
import Layout from "./components/layout/Layout";
import ChatContainer from "./components/chat/ChatContainer";
import InputArea from "./components/chat/InputArea";
import ToolsMenu from "./components/tools/ToolsMenu";
import useChatStore from "./store/chatStore";
import { medicalAPI } from "./api/endpoints";

function App() {
  const {
    messages,
    isLoading,
    addMessage,
    setLoading,
    setError,
    clearMessages,
  } = useChatStore();
  const [showTools, setShowTools] = useState(false);

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
    }
  };

  return (
    <Layout onClearChat={messages.length > 0 ? handleClearChat : null}>
      <div className="h-full flex">
        <div className="flex-1 flex flex-col">
          <ChatContainer messages={messages} isLoading={isLoading} />
          <InputArea
            onSend={handleSendMessage}
            isLoading={isLoading}
            onOpenTools={() => setShowTools(!showTools)}
          />
        </div>

        {showTools && (
          <div className="w-80 border-l border-slate-200 bg-white">
            <ToolsMenu />
          </div>
        )}
      </div>
    </Layout>
  );
}

export default App;
