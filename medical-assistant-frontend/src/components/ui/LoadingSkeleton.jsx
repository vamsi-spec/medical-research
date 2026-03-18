import React from "react";

const LoadingSkeleton = () => {
  return (
    <div className="flex justify-start mb-6 animate-pulse">
      <div className="flex items-start gap-3 max-w-[90%]">
        {/* Avatar skeleton */}
        <div className="w-8 h-8 bg-slate-300 dark:bg-slate-600 rounded-full" />

        <div className="flex-1 space-y-3">
          {/* Main content skeleton */}
          <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-4 space-y-3">
            <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-3/4" />
            <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-full" />
            <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-5/6" />
            <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-2/3" />

            {/* Citations skeleton */}
            <div className="pt-3 border-t border-slate-200 dark:border-slate-700">
              <div className="flex gap-2">
                <div className="w-6 h-6 bg-slate-200 dark:bg-slate-700 rounded" />
                <div className="w-6 h-6 bg-slate-200 dark:bg-slate-700 rounded" />
                <div className="w-6 h-6 bg-slate-200 dark:bg-slate-700 rounded" />
              </div>
            </div>
          </div>

          {/* Metadata skeleton */}
          <div className="flex gap-3">
            <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded w-24" />
            <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded w-20" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoadingSkeleton;
