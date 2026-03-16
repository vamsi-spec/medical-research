import React from "react";
import { User } from "lucide-react";

const UserMessage = ({ message }) => {
  return (
    <div className="flex justify-end mb-4">
      <div className="flex items-start gap-3 max-w-[80%]">
        <div className="bg-blue-700 text-white rounded-lg px-4 py-3 shadow-md">
          <p className="text-sm leading-relaxed">{message}</p>
        </div>
        <div className="flex-shrink-0 w-8 h-8 bg-blue-700 rounded-full flex items-center justify-center">
          <User className="w-5 h-5 text-white" />
        </div>
      </div>
    </div>
  );
};

export default UserMessage;
