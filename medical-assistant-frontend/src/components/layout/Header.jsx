import React from "react";
import { Activity, Trash2 } from "lucide-react";
import Button from "../ui/Button";

const Header = ({ onClearChat }) => {
  return (
    <header className="bg-white border-b border-slate-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-700 rounded-lg flex items-center justify-center">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">
              Medical Research Assistant
            </h1>
            <p className="text-xs text-slate-500">
              Evidence-Based Medical Information
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-500 hidden sm:block">
            Powered by PubMed & AI
          </span>
          {onClearChat && (
            <Button
              variant="secondary"
              onClick={onClearChat}
              className="text-xs"
            >
              <Trash2 className="w-4 h-4 sm:mr-2" />
              <span className="hidden sm:inline">Clear</span>
            </Button>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
