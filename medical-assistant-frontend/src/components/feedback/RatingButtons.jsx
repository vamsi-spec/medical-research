import React, { useState } from "react";
import { ThumbsUp, ThumbsDown } from "lucide-react";
import { showToast } from "../../lib/toast";

const RatingButtons = ({ messageIndex, onRate }) => {
  const [rating, setRating] = useState(null);

  const handleRate = (value) => {
    setRating(value);
    onRate(messageIndex, value);
    showToast.success(
      value === "up" ? "Thanks for the feedback!" : "Feedback recorded",
    );
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => handleRate("up")}
        className={`p-1 rounded transition-colors ${
          rating === "up"
            ? "text-green-600 bg-green-100"
            : "text-slate-400 hover:text-green-600 hover:bg-green-50"
        }`}
        title="Helpful answer"
      >
        <ThumbsUp className="w-4 h-4" />
      </button>

      <button
        onClick={() => handleRate("down")}
        className={`p-1 rounded transition-colors ${
          rating === "down"
            ? "text-red-600 bg-red-100"
            : "text-slate-400 hover:text-red-600 hover:bg-red-50"
        }`}
        title="Not helpful"
      >
        <ThumbsDown className="w-4 h-4" />
      </button>
    </div>
  );
};

export default RatingButtons;
