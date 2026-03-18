import React, { useState, useEffect } from "react";
import { storage } from "../../lib/storage";
import { format } from "date-fns";
import { Bookmark, Trash2, ExternalLink } from "lucide-react";
import Button from "../ui/Button";
import Card from "../ui/Card";
import Badge from "../ui/Badge";
import { showToast } from "../../lib/toast";

const BookmarksPanel = () => {
  const [bookmarks, setBookmarks] = useState([]);

  useEffect(() => {
    loadBookmarks();
  }, []);

  const loadBookmarks = () => {
    const saved = storage.getBookmarks();
    setBookmarks(saved);
  };

  const handleDelete = (bookmarkId) => {
    if (window.confirm("Delete this bookmark?")) {
      storage.deleteBookmark(bookmarkId);
      loadBookmarks();
      showToast.success("Bookmark deleted");
    }
  };

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Bookmark className="w-5 h-5 text-yellow-500" />
          Bookmarked Answers
        </h2>
        <Badge variant="info">{bookmarks.length}</Badge>
      </div>

      {bookmarks.length === 0 ? (
        <div className="text-center py-8 text-slate-500 dark:text-slate-400">
          <Bookmark className="w-12 h-12 mx-auto mb-3 text-slate-300" />
          <p className="text-sm">No bookmarks yet</p>
          <p className="text-xs mt-1">
            Click the bookmark icon on answers to save them
          </p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {bookmarks.map((bookmark) => (
            <Card key={bookmark.id} className="relative">
              <div className="space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <p className="font-medium text-sm text-slate-900 dark:text-white">
                    {bookmark.query}
                  </p>
                  <button
                    onClick={() => handleDelete(bookmark.id)}
                    className="text-slate-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-3">
                  {bookmark.answer}
                </p>

                <div className="flex items-center gap-2 flex-wrap">
                  {bookmark.confidence && (
                    <Badge
                      variant={
                        bookmark.confidence >= 0.85 ? "success" : "warning"
                      }
                    >
                      {Math.round(bookmark.confidence * 100)}% confidence
                    </Badge>
                  )}

                  {bookmark.citations && bookmark.citations.length > 0 && (
                    <Badge variant="info">
                      {bookmark.citations.length} citations
                    </Badge>
                  )}

                  <span className="text-xs text-slate-400 dark:text-slate-500 ml-auto">
                    {format(new Date(bookmark.timestamp), "MMM d, h:mm a")}
                  </span>
                </div>

                {bookmark.citations && bookmark.citations.length > 0 && (
                  <div className="pt-2 border-t border-slate-200 dark:border-slate-700">
                    <p className="text-xs text-slate-500 mb-1">References:</p>
                    <div className="flex flex-wrap gap-1">
                      {bookmark.citations.slice(0, 3).map((citation, idx) => (
                        <a
                          key={idx}
                          href={`https://pubmed.ncbi.nlm.nih.gov/${citation.pmid}/`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-700 dark:text-blue-400 hover:underline flex items-center gap-1"
                        >
                          {citation.pmid}
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default BookmarksPanel;
