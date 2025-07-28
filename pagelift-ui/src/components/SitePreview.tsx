"use client";
import { useState } from "react";

interface SitePreviewProps {
  jobId: string;
  originalUrl?: string;
  mode?: "optimized" | "comparison";
}

export default function SitePreview({ jobId, originalUrl, mode = "optimized" }: SitePreviewProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL;
  const previewUrl = `${API_URL}/jobs/${jobId}/preview`;

  const handleIframeLoad = () => {
    setLoading(false);
  };

  const handleIframeError = () => {
    setLoading(false);
    setError("Failed to load preview");
  };

  if (mode === "comparison" && originalUrl) {
    return (
      <div className="w-full h-full">
        <div className="flex h-12 bg-gray-100 border-b">
          <div className="flex-1 text-center py-3 font-semibold border-r">Original</div>
          <div className="flex-1 text-center py-3 font-semibold">Optimized</div>
        </div>
        <div className="flex h-[calc(100%-3rem)]">
          <div className="flex-1 border-r">
            <iframe
              src={originalUrl}
              className="w-full h-full border-0"
              sandbox="allow-scripts allow-same-origin"
              title="Original Site"
            />
          </div>
          <div className="flex-1 relative">
            {loading && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-50">
                <div className="text-gray-500">Loading optimized preview...</div>
              </div>
            )}
            {error && (
              <div className="absolute inset-0 flex items-center justify-center bg-red-50">
                <div className="text-red-600">{error}</div>
              </div>
            )}
            <iframe
              src={previewUrl}
              className="w-full h-full border-0"
              sandbox="allow-scripts allow-same-origin"
              title="Optimized Site"
              onLoad={handleIframeLoad}
              onError={handleIframeError}
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full relative">
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-50 z-10">
          <div className="text-gray-500">Loading preview...</div>
        </div>
      )}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-red-50 z-10">
          <div className="text-red-600">{error}</div>
        </div>
      )}
      <iframe
        src={previewUrl}
        className="w-full h-full border-0"
        sandbox="allow-scripts allow-same-origin"
        title="Site Preview"
        onLoad={handleIframeLoad}
        onError={handleIframeError}
      />
    </div>
  );
}