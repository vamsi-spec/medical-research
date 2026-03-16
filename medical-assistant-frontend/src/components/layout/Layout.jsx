import React from "react";
import Header from "./Header";

const Layout = ({ children, onClearChat }) => {
  return (
    <div className="h-screen flex flex-col bg-slate-50">
      <Header onClearChat={onClearChat} />
      <main className="flex-1 overflow-hidden">{children}</main>
    </div>
  );
};

export default Layout;
