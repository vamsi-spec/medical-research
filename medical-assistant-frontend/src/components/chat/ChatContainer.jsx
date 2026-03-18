import React, { useRef, useEffect } from "react";
import UserMessage from "./UserMessage";
import AssistantMessage from "./AssistantMessage";
import { Loader2, BookOpen } from "lucide-react";
import LoadingSkeleton from "../ui/LoadingSkeleton";

const ChatContainer = ({ messages, isLoading, onRate }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4">
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full">
          <div className="text-center max-w-md">
            <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <BookOpen className="w-10 h-10 text-blue-700" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">
              Medical Research Assistant
            </h2>
            <p className="text-slate-600 mb-4">
              Ask evidence-based medical questions and get answers backed by
              peer-reviewed research.
            </p>
            <div className="bg-blue-50 rounded-lg p-4 text-left">
              <p className="text-sm font-medium text-blue-900 mb-2">
                Example questions:
              </p>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• What is the first-line treatment for type 2 diabetes?</li>
                <li>• How does metformin work?</li>
                <li>• What are the side effects of statins?</li>
              </ul>
            </div>
          </div>
        </div>
      ) : (
        <>
          {messages.map((message, index) => (
            <div key={index}>
              {message.type === "user" ? (
                <UserMessage message={message.content} />
              ) : (
                <AssistantMessage
                  data={message.data}
                  messageIndex={index}
                  onRate={onRate}
                  query={message.query}
                />
              )}
            </div>
          ))}

          {isLoading && <LoadingSkeleton />}
        </>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatContainer;
