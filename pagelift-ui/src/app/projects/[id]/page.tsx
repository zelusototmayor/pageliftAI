"use client";
import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import SitePreview from "@/components/SitePreview";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

function fetchProject(projectId: string) {
  return fetch(`${API_URL}/projects`).then((res) => {
    if (!res.ok) throw new Error("Failed to fetch projects");
    return res.json();
  }).then((projects) => {
    const project = projects.find((p: any) => p.id.toString() === projectId);
    if (!project) throw new Error("Project not found");
    return project;
  });
}

type TabType = "status" | "preview" | "compare";

export default function ProjectStatusPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params?.id as string;
  const [activeTab, setActiveTab] = useState<TabType>("status");
  
  const {
    data: project,
    error,
    isLoading,
  } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => fetchProject(projectId),
    refetchInterval: 2000,
    enabled: !!projectId,
  });

  const isComplete = project?.status === "complete";
  const canPreview = isComplete && project?.download_url;

  const tabs = [
    { id: "status" as TabType, label: "Status", enabled: true },
    { id: "preview" as TabType, label: "Preview", enabled: canPreview },
    { id: "compare" as TabType, label: "Compare", enabled: canPreview && project?.url },
  ];

  return (
    <div className="max-w-6xl mx-auto py-10 px-4">
      <div className="mb-6">
        <button
          onClick={() => router.back()}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4 transition-colors"
        >
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L4.414 9H17a1 1 0 110 2H4.414l5.293 5.293a1 1 0 010 1.414z" clipRule="evenodd" />
          </svg>
          Back to Dashboard
        </button>
        <h1 className="text-3xl font-bold mb-2">
          {project?.name || 'Project Details'}
        </h1>
        {project?.url && (
          <p className="text-gray-600">
            <a href={project.url} target="_blank" rel="noopener noreferrer" className="hover:text-blue-600">
              {project.url}
            </a>
          </p>
        )}
      </div>
      
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
          {isLoading && <div className="text-gray-500">Loading project details...</div>}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="text-red-800 font-medium">Error loading project</div>
              <div className="text-red-600 text-sm mt-1">{(error as Error).message}</div>
            </div>
          )}
          {project && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <span className="font-semibold text-gray-700">Project ID:</span>
                  <div className="text-gray-900">{project.id}</div>
                </div>
                <div>
                  <span className="font-semibold text-gray-700">Project Name:</span>
                  <div className="text-gray-900">{project.name}</div>
                </div>
                <div>
                  <span className="font-semibold text-gray-700">Original URL:</span>
                  <div>
                    <a href={project.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                      {project.url}
                    </a>
                  </div>
                </div>
                <div>
                  <span className="font-semibold text-gray-700">Status:</span>
                  <div className="mt-1">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      project.status === 'complete' ? 'bg-green-100 text-green-800' :
                      project.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                      project.status === 'queued' ? 'bg-yellow-100 text-yellow-800' :
                      project.status === 'failed' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {project.status || 'Unknown'}
                    </span>
                  </div>
                </div>
                {project.job_id && (
                  <div>
                    <span className="font-semibold text-gray-700">Job ID:</span>
                    <div className="text-gray-900">{project.job_id}</div>
                  </div>
                )}
              </div>
              
              {project.error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="font-medium text-red-800">Error Details:</div>
                  <div className="text-red-600 text-sm mt-1">{project.error}</div>
                </div>
              )}
              
              {project.status === "complete" && project.download_url && (
                <div className="flex gap-3 pt-4 border-t">
                  <a
                    href={`${API_URL}/jobs/${project.job_id}/download`}
                    className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    download
                  >
                    <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                    Download ZIP
                  </a>
                  <a
                    href={`${API_URL}/jobs/${project.job_id}/preview`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                      <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd"/>
                    </svg>
                    Preview Site
                  </a>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === "preview" && canPreview && (
        <div className="bg-white shadow rounded-lg overflow-hidden" style={{ height: "70vh" }}>
          <SitePreview jobId={project.job_id.toString()} mode="optimized" />
        </div>
      )}

      {activeTab === "compare" && canPreview && project?.url && (
        <div className="bg-white shadow rounded-lg overflow-hidden" style={{ height: "70vh" }}>
          <SitePreview jobId={project.job_id.toString()} originalUrl={project.url} mode="comparison" />
        </div>
      )}
    </div>
  );
} 