import React from "react";
import { Loader2 } from "lucide-react";

const Button = ({
  children,
  onClick,
  disabled = false,
  loading = false,
  variant = "primary",
  className = "",
  type = "button",
  ...props
}) => {
  const baseStyles = "medical-button";
  const variantStyles = {
    primary: "medical-button-primary",
    secondary: "bg-slate-100 text-slate-700 hover:bg-slate-200",
    danger: "bg-red-600 text-white hover:bg-red-700",
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`${baseStyles} ${variantStyles[variant]} ${className} ${
        disabled || loading ? "opacity-50 cursor-not-allowed" : ""
      }`}
      {...props}
    >
      {loading ? (
        <span className="flex items-center gap-2">
          <Loader2 className="w-4 h-4 animate-spin" />
          Loading...
        </span>
      ) : (
        children
      )}
    </button>
  );
};

export default Button;
