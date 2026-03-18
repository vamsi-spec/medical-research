export const storage = {
  // Chat History
  saveChat: (chat) => {
    const chats = storage.getChats();
    const newChat = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      ...chat,
    };
    chats.unshift(newChat);
    localStorage.setItem("medical_chats", JSON.stringify(chats.slice(0, 50))); // Keep last 50
    return newChat;
  },

  getChats: () => {
    const chats = localStorage.getItem("medical_chats");
    return chats ? JSON.parse(chats) : [];
  },

  deleteChat: (chatId) => {
    const chats = storage.getChats();
    const filtered = chats.filter((chat) => chat.id !== chatId);
    localStorage.setItem("medical_chats", JSON.stringify(filtered));
  },

  clearAllChats: () => {
    localStorage.removeItem("medical_chats");
  },

  // Bookmarks
  saveBookmark: (bookmark) => {
    const bookmarks = storage.getBookmarks();
    const newBookmark = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      ...bookmark,
    };
    bookmarks.unshift(newBookmark);
    localStorage.setItem("medical_bookmarks", JSON.stringify(bookmarks));
    return newBookmark;
  },

  getBookmarks: () => {
    const bookmarks = localStorage.getItem("medical_bookmarks");
    return bookmarks ? JSON.parse(bookmarks) : [];
  },

  deleteBookmark: (bookmarkId) => {
    const bookmarks = storage.getBookmarks();
    const filtered = bookmarks.filter((b) => b.id !== bookmarkId);
    localStorage.setItem("medical_bookmarks", JSON.stringify(filtered));
  },

  // Settings
  getSettings: () => {
    const settings = localStorage.getItem("medical_settings");
    return settings
      ? JSON.parse(settings)
      : {
          darkMode: false,
          autoScroll: true,
          citationFormat: "APA",
          showConfidence: true,
          disclaimerAccepted: false,
        };
  },

  saveSettings: (settings) => {
    localStorage.setItem("medical_settings", JSON.stringify(settings));
  },

  // Disclaimer
  acceptDisclaimer: () => {
    const settings = storage.getSettings();
    settings.disclaimerAccepted = true;
    storage.saveSettings(settings);
  },

  hasAcceptedDisclaimer: () => {
    const settings = storage.getSettings();
    return settings.disclaimerAccepted;
  },
};
