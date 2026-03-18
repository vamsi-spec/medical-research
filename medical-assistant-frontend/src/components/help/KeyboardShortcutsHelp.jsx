import React from "react";
import Modal from "../ui/Modal";
import { Command } from "lucide-react";

const KeyboardShortcutsHelp = ({ isOpen, onClose }) => {
  const isMac = navigator.platform.toUpperCase().indexOf("MAC") >= 0;
  const modKey = isMac ? "⌘" : "Ctrl";

  const shortcuts = [
    { keys: `${modKey} + K`, action: "Focus search input" },
    { keys: `${modKey} + N`, action: "Start new chat" },
    { keys: `${modKey} + E`, action: "Export conversation" },
    { keys: `${modKey} + B`, action: "Toggle bookmarks" },
    { keys: `${modKey} + H`, action: "Toggle chat history" },
    { keys: `${modKey} + ,`, action: "Open settings" },
    { keys: "Escape", action: "Close modals" },
    { keys: "Enter", action: "Send message" },
    { keys: "Shift + Enter", action: "New line in message" },
  ];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Keyboard Shortcuts"
      size="sm"
    >
      <div className="space-y-2">
        {shortcuts.map((shortcut, idx) => (
          <div
            key={idx}
            className="flex items-center justify-between py-2 border-b border-slate-200 dark:border-slate-700 last:border-0"
          >
            <span className="text-sm text-slate-700 dark:text-slate-300">
              {shortcut.action}
            </span>
            <kbd className="px-2 py-1 text-xs font-mono bg-slate-100 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded">
              {shortcut.keys}
            </kbd>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
          <Command className="w-4 h-4" />
          <span>Press ? to show this help anytime</span>
        </div>
      </div>
    </Modal>
  );
};

export default KeyboardShortcutsHelp;
