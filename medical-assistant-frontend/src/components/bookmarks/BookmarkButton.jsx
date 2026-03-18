import React, { useState, useEffect } from "react";
import { Bookmark } from "lucide-react";
import { storage } from "../../lib/storage";
import { showToast } from "../../lib/toast";

const BookmarkButton = ({ message, messageIndex }) => {
  const [isBookmarked, setIsBookmarked] = useState(false);

  useEffect(() => {
    const bookmarks = storage.getBookmarks();
    const exists = bookmarks.some(
      (b) =>
        b.messageIndex === messageIndex && b.answer === message.data.answer,
    );
    setIsBookmarked(exists);
  }, [message, messageIndex]);

  const handleToggleBookmark = () => {
    if (isBookmarked) {
      // Remove bookmark
      const bookmarks = storage.getBookmarks();
      const filtered = bookmarks.filter(
        (b) =>
          !(
            b.messageIndex === messageIndex && b.answer === message.data.answer
          ),
      );
      localStorage.setItem("medical_bookmarks", JSON.stringify(filtered));
      setIsBookmarked(false);
      showToast.info("Bookmark removed");
    } else {
      // Add bookmark
      storage.saveBookmark({
        messageIndex,
        query: message.query || "Unknown query",
        answer: message.data.answer,
        citations: message.data.citations,
        confidence: message.data.confidence,
      });
      setIsBookmarked(true);
      showToast.success("Answer bookmarked");
    }
  };

  return (
    <button
      onClick={handleToggleBookmark}
      className={`p-2 rounded hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors ${
        isBookmarked ? "text-yellow-500" : "text-slate-400"
      }`}
      title={isBookmarked ? "Remove bookmark" : "Bookmark this answer"}
    >
      <Bookmark className={`w-4 h-4 ${isBookmarked ? "fill-current" : ""}`} />
    </button>
  );
};

export default BookmarkButton;
