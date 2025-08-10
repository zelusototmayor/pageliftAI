"use client";
import React, { useState } from "react";

interface SitePreviewProps {
  jobId: string;
  originalUrl?: string;
  mode?: "optimized" | "comparison";
}

type ViewportSize = "desktop" | "tablet" | "mobile";

const viewportSizes = {
  desktop: { width: "100%", height: "100%", label: "Desktop", icon: "🖥️" },
  tablet: { width: "768px", height: "100%", label: "Tablet", icon: "📱" },
  mobile: { width: "375px", height: "100%", label: "Mobile", icon: "📱" }
};

export default function SitePreview({ jobId, originalUrl, mode = "optimized" }: SitePreviewProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewport, setViewport] = useState<ViewportSize>("desktop");
  const [showQualityMetrics, setShowQualityMetrics] = useState(false);

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
      <div className="w-full h-full flex flex-col">
        {/* Comparison Toolbar */}
        <div className="flex items-center justify-between p-4 bg-gray-100 border-b border-gray-200">
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-gray-700">Comparison View</span>
            <div className="flex bg-white border border-gray-300 rounded-md">
              {Object.entries(viewportSizes).map(([key, config]) => (
                <button
                  key={key}
                  onClick={() => setViewport(key as ViewportSize)}
                  className={`px-3 py-1.5 text-xs font-medium transition-colors ${
                    viewport === key
                      ? "bg-blue-500 text-white"
                      : "text-gray-600 hover:bg-gray-50"
                  } ${key === 'desktop' ? 'rounded-l-md' : key === 'mobile' ? 'rounded-r-md' : ''}`}
                >
                  <span className="mr-1">{config.icon}</span>
                  {config.label}
                </button>
              ))}
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowQualityMetrics(!showQualityMetrics)}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                showQualityMetrics
                  ? "bg-green-100 text-green-700"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              📊 Quality Metrics
            </button>
          </div>
        </div>

        <div className="flex-1 flex">
          <div className="flex-1 flex">
            {/* Comparison Headers */}
            <div className="flex w-full h-12 bg-gray-50 border-b">
              <div className="flex-1 text-center py-3 font-semibold border-r text-gray-700">
                Original Website
              </div>
              <div className="flex-1 text-center py-3 font-semibold text-gray-700">
                Optimized Website
              </div>
            </div>
          </div>
        </div>

        <div className="flex-1 flex">
          <div className="flex-1 flex">
            {/* Original vs Optimized */}
            <div className="flex-1 border-r bg-gray-100 flex justify-center">
              <div 
                className="bg-white shadow-lg transition-all duration-300"
                style={{ 
                  width: viewportSizes[viewport].width,
                  height: "100%",
                  maxWidth: "100%"
                }}
              >
                <iframe
                  src={originalUrl}
                  className="w-full h-full border-0"
                  sandbox="allow-scripts allow-same-origin"
                  title="Original Site"
                />
              </div>
            </div>
            <div className="flex-1 relative bg-gray-100 flex justify-center">
              <div 
                className="bg-white shadow-lg transition-all duration-300"
                style={{ 
                  width: viewportSizes[viewport].width,
                  height: "100%",
                  maxWidth: "100%"
                }}
              >
                {loading && (
                  <div className="absolute inset-0 flex items-center justify-center bg-gray-50">
                    <div className="flex items-center gap-2 text-gray-500">
                      <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Loading optimized preview...
                    </div>
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
          
          {/* Quality Metrics Sidebar for Comparison */}
          {showQualityMetrics && (
            <div className="w-80 bg-white border-l border-gray-200 p-4 overflow-y-auto">
              <QualityMetrics jobId={jobId} />
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full flex flex-col">
      {/* Preview Toolbar */}
      <div className="flex items-center justify-between p-4 bg-gray-100 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700">View:</span>
          <div className="flex bg-white border border-gray-300 rounded-md">
            {Object.entries(viewportSizes).map(([key, config]) => (
              <button
                key={key}
                onClick={() => setViewport(key as ViewportSize)}
                className={`px-3 py-1.5 text-xs font-medium transition-colors ${
                  viewport === key
                    ? "bg-blue-500 text-white"
                    : "text-gray-600 hover:bg-gray-50"
                } ${key === 'desktop' ? 'rounded-l-md' : key === 'mobile' ? 'rounded-r-md' : ''}`}
              >
                <span className="mr-1">{config.icon}</span>
                {config.label}
              </button>
            ))}
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowQualityMetrics(!showQualityMetrics)}
            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
              showQualityMetrics
                ? "bg-green-100 text-green-700"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            📊 Quality Metrics
          </button>
          <a
            href={previewUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-1.5 text-xs font-medium bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
          >
            🔗 Open in New Tab
          </a>
        </div>
      </div>

      <div className="flex-1 flex">
        {/* Main Preview Area */}
        <div className="flex-1 relative bg-gray-100">
          <div 
            className="mx-auto bg-white shadow-lg transition-all duration-300"
            style={{ 
              width: viewportSizes[viewport].width,
              height: "100%",
              maxWidth: "100%"
            }}
          >
            {loading && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-50 z-10">
                <div className="flex items-center gap-2 text-gray-500">
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Loading preview...
                </div>
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
        </div>

        {/* Quality Metrics Sidebar */}
        {showQualityMetrics && (
          <div className="w-80 bg-white border-l border-gray-200 p-4 overflow-y-auto">
            <QualityMetrics jobId={jobId} />
          </div>
        )}
      </div>
    </div>
  );
}

// Quality Metrics Component
interface QualityMetricsProps {
  jobId: string;
}

function QualityMetrics({ jobId }: QualityMetricsProps) {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [rating, setRating] = useState<number>(0);

  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  // Load quality metrics from API
  React.useEffect(() => {
    const loadMetrics = async () => {
      try {
        const response = await fetch(`${API_URL}/debug/job/${jobId}/quality-report`);
        const data = await response.json();
        
        if (!data.error) {
          setMetrics(data);
        }
      } catch (error) {
        console.error('Failed to load quality metrics:', error);
      } finally {
        setLoading(false);
      }
    };

    loadMetrics();
  }, [jobId, API_URL]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="flex items-center gap-2 text-gray-500 text-sm">
          <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Loading metrics...
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-500 text-sm mb-4">
          Quality metrics not available for this job.
        </div>
        <p className="text-xs text-gray-400">
          Metrics are generated during processing and may not be available for older jobs.
        </p>
      </div>
    );
  }

  const overallScore = metrics.quality_scores?.overall_quality_score || 0;
  const grade = metrics.quality_grade || 'N/A';

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Quality Report</h3>
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-green-500 text-white text-xl font-bold">
          {grade}
        </div>
        <div className="text-sm text-gray-600 mt-1">Overall Score: {overallScore.toFixed(1)}%</div>
      </div>

      {/* Content Metrics */}
      <div className="space-y-3">
        <h4 className="font-medium text-gray-900">Content Analysis</h4>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Total Sections:</span>
            <span className="font-medium">{metrics.metrics?.total_sections || 0}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Total Words:</span>
            <span className="font-medium">{metrics.metrics?.total_words || 0}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Images Found:</span>
            <span className="font-medium">{metrics.metrics?.total_images || 0}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Avg Words/Section:</span>
            <span className="font-medium">{metrics.metrics?.average_words_per_section || 0}</span>
          </div>
        </div>
      </div>

      {/* Business Data */}
      <div className="space-y-3">
        <h4 className="font-medium text-gray-900">Business Information</h4>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Phone Numbers:</span>
            <span className="font-medium">{metrics.business_data?.phones_found || 0}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Email Addresses:</span>
            <span className="font-medium">{metrics.business_data?.emails_found || 0}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Call-to-Actions:</span>
            <span className="font-medium">{metrics.business_data?.ctas_found || 0}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Forms:</span>
            <span className="font-medium">{metrics.business_data?.forms_found || 0}</span>
          </div>
        </div>
      </div>

      {/* Quality Scores */}
      <div className="space-y-3">
        <h4 className="font-medium text-gray-900">Quality Breakdown</h4>
        <div className="space-y-2">
          <ScoreBar 
            label="Content Density" 
            score={metrics.quality_scores?.content_density_score || 0} 
          />
          <ScoreBar 
            label="Business Completeness" 
            score={metrics.quality_scores?.business_completeness_score || 0} 
          />
        </div>
      </div>

      {/* User Rating */}
      <div className="space-y-3 border-t border-gray-200 pt-4">
        <h4 className="font-medium text-gray-900">Rate This Website</h4>
        <div className="flex items-center justify-center gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              onClick={() => setRating(star)}
              className={`text-2xl transition-colors ${
                star <= rating ? "text-yellow-400" : "text-gray-300 hover:text-yellow-300"
              }`}
            >
              ⭐
            </button>
          ))}
        </div>
        {rating > 0 && (
          <div className="text-center">
            <button className="text-xs bg-blue-100 text-blue-700 px-3 py-1 rounded-full hover:bg-blue-200 transition-colors">
              Submit Rating
            </button>
          </div>
        )}
      </div>

      {/* Issues & Recommendations */}
      {(metrics.issues?.length > 0 || metrics.recommendations?.length > 0) && (
        <div className="space-y-3 border-t border-gray-200 pt-4">
          {metrics.issues?.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Issues Found</h4>
              <ul className="space-y-1">
                {metrics.issues.slice(0, 3).map((issue: string, index: number) => (
                  <li key={index} className="text-xs text-red-600 flex items-start gap-1">
                    <span className="text-red-500 mt-0.5">⚠️</span>
                    <span>{issue}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {metrics.recommendations?.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Recommendations</h4>
              <ul className="space-y-1">
                {metrics.recommendations.slice(0, 3).map((rec: string, index: number) => (
                  <li key={index} className="text-xs text-green-600 flex items-start gap-1">
                    <span className="text-green-500 mt-0.5">💡</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Score Bar Component
interface ScoreBarProps {
  label: string;
  score: number;
}

function ScoreBar({ label, score }: ScoreBarProps) {
  const percentage = Math.min(100, Math.max(0, score));
  const color = percentage >= 80 ? 'bg-green-500' : percentage >= 60 ? 'bg-yellow-500' : 'bg-red-500';
  
  return (
    <div>
      <div className="flex justify-between text-xs text-gray-600 mb-1">
        <span>{label}</span>
        <span>{percentage.toFixed(1)}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className={`h-2 rounded-full transition-all duration-300 ${color}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}