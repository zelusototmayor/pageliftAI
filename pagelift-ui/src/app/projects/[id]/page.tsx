"use client";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { useState } from "react";
import SitePreview from "@/components/SitePreview";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

function fetchJob(id: string) {
  return fetch(`${API_URL}/jobs/${id}`).then((res) => {
    if (!res.ok) throw new Error("Failed to fetch job");
    return res.json();
  });
}

type TabType = "status" | "preview" | "compare";

export default function ProjectStatusPage() {
  const params = useParams();
  const id = params?.id as string;
  const [activeTab, setActiveTab] = useState<TabType>("status");
  
  const {
    data,
    error,
    isLoading,
  } = useQuery({
    queryKey: ["job", id],
    queryFn: () => fetchJob(id),
    refetchInterval: 2000,
    enabled: !!id,
  });

  const isComplete = data?.status === "complete";
  const canPreview = isComplete && data?.download_url;

  const tabs = [
    { id: "status" as TabType, label: "Status", enabled: true },
    { id: "preview" as TabType, label: "Preview", enabled: canPreview },
    { id: "compare" as TabType, label: "Compare", enabled: canPreview && data?.original_url },
  ];

  return (
    <div className="max-w-6xl mx-auto py-10">
      <h1 className="text-2xl font-bold mb-4">Project Status</h1>
      
      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => tab.enabled && setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? "border-blue-500 text-blue-600"
                  : tab.enabled
                  ? "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  : "border-transparent text-gray-300 cursor-not-allowed"
              }`}
              disabled={!tab.enabled}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === "status" && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="mb-2">
            <span className="font-semibold">Job ID:</span> {id}
          </div>
          {isLoading && <div className="text-gray-500">Loading...</div>}
          {error && (
            <div className="text-red-600">Error: {(error as Error).message}</div>
          )}
          {data && (
            <>
              <div className="mb-2">
                <span className="font-semibold">Status:</span> {data.status}
              </div>
              {data.original_url && (
                <div className="mb-2">
                  <span className="font-semibold">Original URL:</span>{" "}
                  <a href={data.original_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                    {data.original_url}
                  </a>
                </div>
              )}
              {data.error && (
                <div className="text-red-600 mb-2">Error: {data.error}</div>
              )}
              {data.status === "complete" && data.download_url && (
                <a
                  href={data.download_url}
                  className="inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
                  download
                >
                  Download ZIP
                </a>
              )}
            </>
          )}
        </div>
      )}

      {activeTab === "preview" && canPreview && (
        <div className="bg-white shadow rounded-lg overflow-hidden" style={{ height: "70vh" }}>
          <SitePreview jobId={id} mode="optimized" />
        </div>
      )}

      {activeTab === "compare" && canPreview && data?.original_url && (
        <div className="bg-white shadow rounded-lg overflow-hidden" style={{ height: "70vh" }}>
          <SitePreview jobId={id} originalUrl={data.original_url} mode="comparison" />
        </div>
      )}
    </div>
  );
} 