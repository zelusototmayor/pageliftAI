"use client";
import Link from "next/link";
import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { getProjects, Project, createProject } from "@/lib/api";
import CreateProjectForm from "@/components/CreateProjectForm";

function StatusBadge({ status }: { status: string }) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'complete':
        return 'bg-green-100 text-green-800';
      case 'queued':
        return 'bg-yellow-100 text-yellow-800';
      case 'scraping':
        return 'bg-blue-100 text-blue-800';
      case 'analyzing':
        return 'bg-purple-100 text-purple-800';
      case 'rendering':
        return 'bg-indigo-100 text-indigo-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'no_job':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'complete':
        return 'Complete';
      case 'queued':
        return 'Queued';
      case 'scraping':
        return 'Scraping Website';
      case 'analyzing':
        return 'Analyzing Content';
      case 'rendering':
        return 'Generating Site';
      case 'processing':
        return 'Processing';
      case 'failed':
        return 'Failed';
      case 'no_job':
        return 'No Job';
      default:
        return 'Unknown';
    }
  };

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(status)}`}>
      {getStatusText(status)}
    </span>
  );
}

export default function DashboardPage() {
  const queryClient = useQueryClient();
  const [retryingProjects, setRetryingProjects] = useState<Set<number>>(new Set());
  
  const { data: projects, isLoading, error } = useQuery<Project[]>({
    queryKey: ["projects"],
    queryFn: getProjects,
  });

  const handleRetryProject = async (project: any) => {
    if (retryingProjects.has(project.id)) return;
    
    setRetryingProjects(prev => new Set([...prev, project.id]));
    
    try {
      await createProject({
        url: project.url,
        project_name: `${project.name} (Retry)`
      });
      
      // Refresh the projects list
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    } catch (error) {
      console.error('Retry failed:', error);
      alert('Failed to retry project. Please try again.');
    } finally {
      setRetryingProjects(prev => {
        const newSet = new Set(prev);
        newSet.delete(project.id);
        return newSet;
      });
    }
  };

  return (
    <div className="max-w-6xl mx-auto py-10 px-4">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Projects Dashboard</h1>
      </div>
      <CreateProjectForm onSuccess={() => queryClient.invalidateQueries({ queryKey: ["projects"] })} />
      <div className="bg-white shadow rounded-lg p-6">
        {isLoading && <div className="text-gray-500">Loading projects...</div>}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <span className="font-medium text-red-800">Error loading projects</span>
            </div>
            <p className="text-red-600 text-sm mt-1">
              Unable to connect to the API. Please check if the backend is running and try refreshing the page.
            </p>
          </div>
        )}
        {projects && projects.length === 0 && (
          <div className="text-gray-500 text-center py-8">
            No projects yet. Create your first project above!
          </div>
        )}
        {projects && projects.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <div key={project.id} className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
                {/* Project Header */}
                <div className="p-6 border-b border-gray-100">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-semibold text-gray-900 truncate">
                        {project.name}
                      </h3>
                      <p className="text-sm text-gray-500 truncate mt-1">
                        <a 
                          href={project.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="hover:text-blue-600 transition-colors"
                          title={project.url}
                        >
                          {project.url}
                        </a>
                      </p>
                    </div>
                    <div className="ml-2 flex-shrink-0">
                      <div className="flex items-center gap-2">
                        <StatusBadge status={project.status || 'unknown'} />
                        {['queued', 'scraping', 'analyzing', 'rendering', 'processing'].includes(project.status || '') && (
                          <svg className="w-4 h-4 animate-spin text-blue-500" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Error Display */}
                  {project.error && (
                    <details className="cursor-pointer mt-3">
                      <summary className="text-xs text-red-600 hover:text-red-800 flex items-center gap-1">
                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                        View Error Details
                      </summary>
                      <div className="text-xs text-red-600 mt-2 p-3 bg-red-50 rounded border border-red-200">
                        {project.error.includes('Name or service not known') ? (
                          <>
                            <div className="font-medium">Website not accessible</div>
                            <div className="mt-1">The website URL couldn't be reached. Please check the URL and try again.</div>
                          </>
                        ) : project.error.includes('timeout') || project.error.includes('Timeout') ? (
                          <>
                            <div className="font-medium">Request timeout</div>
                            <div className="mt-1">The website took too long to respond. Please try again or use a different URL.</div>
                          </>
                        ) : (
                          <>
                            <div className="font-medium">Processing error</div>
                            <div className="mt-1 break-all">{project.error}</div>
                          </>
                        )}
                      </div>
                    </details>
                  )}
                </div>

                {/* Project Actions */}
                <div className="px-6 py-4">
                  <div className="flex flex-wrap gap-2">
                    <Link
                      href={`/projects/${project.id}`}
                      className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
                    >
                      <svg className="w-4 h-4 mr-1.5" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                        <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd"/>
                      </svg>
                      View Details
                    </Link>
                    
                    {project.status === 'complete' && project.download_url && (
                      <>
                        <a
                          href={`${process.env.NEXT_PUBLIC_API_URL}/jobs/${project.job_id}/preview`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-green-700 bg-green-100 rounded-md hover:bg-green-200 transition-colors"
                        >
                          <svg className="w-4 h-4 mr-1.5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd"/>
                          </svg>
                          Preview
                        </a>
                        <a
                          href={`${process.env.NEXT_PUBLIC_API_URL}/jobs/${project.job_id}/download`}
                          download
                          className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-purple-700 bg-purple-100 rounded-md hover:bg-purple-200 transition-colors"
                        >
                          <svg className="w-4 h-4 mr-1.5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd"/>
                          </svg>
                          Download
                        </a>
                      </>
                    )}
                    
                    {project.status === 'failed' && (
                      <button
                        onClick={() => handleRetryProject(project)}
                        disabled={retryingProjects.has(project.id)}
                        className={`inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                          retryingProjects.has(project.id)
                            ? "text-gray-500 bg-gray-100 cursor-not-allowed"
                            : "text-orange-700 bg-orange-100 hover:bg-orange-200"
                        }`}
                      >
                        {retryingProjects.has(project.id) ? (
                          <>
                            <svg className="w-4 h-4 mr-1.5 animate-spin" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Retrying...
                          </>
                        ) : (
                          <>
                            <svg className="w-4 h-4 mr-1.5" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd"/>
                            </svg>
                            Retry
                          </>
                        )}
                      </button>
                    )}
                  </div>
                </div>

                {/* Project Metadata */}
                <div className="px-6 py-3 bg-gray-50 border-t border-gray-100 rounded-b-lg">
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>ID: {project.id}</span>
                    {project.job_id && <span>Job: {project.job_id}</span>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
} 