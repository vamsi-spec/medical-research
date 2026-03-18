import { useEffect } from "react";

export const useKeyboardShortcuts = (handlers) => {
  useEffect(() => {
    const handleKeyDown = (e) => {
      const isMac = navigator.platform.toUpperCase().indexOf("MAC") >= 0;
      const modKey = isMac ? e.metaKey : e.ctrlKey;

      // Ctrl/Cmd + K: Focus search
      if (modKey && e.key === "k") {
        e.preventDefault();
        handlers.onFocusSearch?.();
      }

      // Ctrl/Cmd + N: New chat
      if (modKey && e.key === "n") {
        e.preventDefault();
        handlers.onNewChat?.();
      }

      // Ctrl/Cmd + E: Export
      if (modKey && e.key === "e") {
        e.preventDefault();
        handlers.onExport?.();
      }

      // Ctrl/Cmd + B: Toggle bookmarks
      if (modKey && e.key === "b") {
        e.preventDefault();
        handlers.onToggleBookmarks?.();
      }

      // Ctrl/Cmd + H: Toggle history
      if (modKey && e.key === "h") {
        e.preventDefault();
        handlers.onToggleHistory?.();
      }

      // Ctrl/Cmd + ,: Settings
      if (modKey && e.key === ",") {
        e.preventDefault();
        handlers.onOpenSettings?.();
      }

      // Escape: Close modals
      if (e.key === "Escape") {
        handlers.onEscape?.();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handlers]);
};
