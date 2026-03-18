import React, { useState, useEffect } from "react";
import Modal from "../ui/Modal";
import Button from "../ui/Button";
import { storage } from "../../lib/storage";
import { showToast } from "../../lib/toast";
import { useTheme } from "../../contexts/ThemeContext";
import { Moon, Sun } from "lucide-react";

const SettingsModal = ({ isOpen, onClose }) => {
  const { darkMode, toggleDarkMode } = useTheme();
  const [settings, setSettings] = useState(storage.getSettings());

  useEffect(() => {
    if (isOpen) {
      setSettings(storage.getSettings());
    }
  }, [isOpen]);

  const handleSave = () => {
    storage.saveSettings(settings);
    showToast.success("Settings saved");
    onClose();
  };

  const handleToggle = (key) => {
    setSettings((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Settings" size="md">
      <div className="space-y-6">
        {/* Appearance */}
        <div>
          <h3 className="font-bold text-slate-900 dark:text-white mb-3">
            Appearance
          </h3>

          <div className="space-y-3">
            {/* Dark Mode */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {darkMode ? (
                  <Moon className="w-5 h-5" />
                ) : (
                  <Sun className="w-5 h-5" />
                )}
                <div>
                  <p className="font-medium text-slate-900 dark:text-white">
                    Dark Mode
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Toggle dark theme
                  </p>
                </div>
              </div>
              <button
                onClick={toggleDarkMode}
                className={`relative w-12 h-6 rounded-full transition-colors ${
                  darkMode ? "bg-blue-700" : "bg-slate-300"
                }`}
              >
                <div
                  className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
                    darkMode ? "transform translate-x-6" : ""
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* Behavior */}
        <div>
          <h3 className="font-bold text-slate-900 dark:text-white mb-3">
            Behavior
          </h3>

          <div className="space-y-3">
            {/* Auto Scroll */}
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-slate-900 dark:text-white">
                  Auto-scroll
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Automatically scroll to new messages
                </p>
              </div>
              <button
                onClick={() => handleToggle("autoScroll")}
                className={`relative w-12 h-6 rounded-full transition-colors ${
                  settings.autoScroll ? "bg-blue-700" : "bg-slate-300"
                }`}
              >
                <div
                  className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
                    settings.autoScroll ? "transform translate-x-6" : ""
                  }`}
                />
              </button>
            </div>

            {/* Show Confidence */}
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-slate-900 dark:text-white">
                  Show Confidence Scores
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Display confidence indicators
                </p>
              </div>
              <button
                onClick={() => handleToggle("showConfidence")}
                className={`relative w-12 h-6 rounded-full transition-colors ${
                  settings.showConfidence ? "bg-blue-700" : "bg-slate-300"
                }`}
              >
                <div
                  className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
                    settings.showConfidence ? "transform translate-x-6" : ""
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* Citations */}
        <div>
          <h3 className="font-bold text-slate-900 dark:text-white mb-3">
            Citations
          </h3>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Default Citation Format
            </label>
            <select
              value={settings.citationFormat}
              onChange={(e) =>
                setSettings((prev) => ({
                  ...prev,
                  citationFormat: e.target.value,
                }))
              }
              className="medical-input"
            >
              <option value="APA">APA</option>
              <option value="BibTeX">BibTeX</option>
              <option value="RIS">RIS</option>
            </select>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-4 border-t border-slate-200 dark:border-slate-700">
          <Button variant="secondary" onClick={onClose} className="flex-1">
            Cancel
          </Button>
          <Button onClick={handleSave} className="flex-1">
            Save Settings
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default SettingsModal;
