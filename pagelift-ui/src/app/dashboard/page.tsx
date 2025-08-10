"use client";
import Link from "next/link";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { getProjects, Project } from "@/lib/api";
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
  const { data: projects, isLoading, error } = useQuery<Project[]>({
    queryKey: ["projects"],
    queryFn: getProjects,
  });

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
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b">
                  <th className="py-3 font-semibold">Project Name</th>
                  <th className="py-3 font-semibold">URL</th>
                  <th className="py-3 font-semibold">Status</th>
                  <th className="py-3 font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((project) => (
                  <tr key={project.id} className="border-t hover:bg-gray-50">
                    <td className="py-3 font-medium">{project.name}</td>
                    <td className="py-3 text-gray-600 max-w-xs truncate">
                      <a 
                        href={project.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="hover:text-blue-600"
                      >
                        {project.url}
                      </a>
                    </td>
                    <td className="py-3">
                      <div className="flex flex-col gap-1">
                        <div className="flex items-center gap-2">
                          <StatusBadge status={project.status || 'unknown'} />
                          {['queued', 'scraping', 'analyzing', 'rendering', 'processing'].includes(project.status || '') && (
                            <svg className="w-4 h-4 animate-spin text-blue-500" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                          )}
                        </div>
                        {project.error && (
                          <details className="cursor-pointer">
                            <summary className="text-xs text-red-600 hover:text-red-800">
                              ⚠️ Error Details
                            </summary>
                            <div className="text-xs text-red-600 mt-1 p-2 bg-red-50 rounded border-l-2 border-red-200 max-w-sm">
                              {project.error.includes('Name or service not known') ? (
                                <>
                                  <div className="font-medium">Website not accessible</div>
                                  <div>The website URL couldn't be reached. Please check the URL and try again.</div>
                                </>
                              ) : project.error.includes('timeout') || project.error.includes('Timeout') ? (
                                <>
                                  <div className="font-medium">Request timeout</div>
                                  <div>The website took too long to respond. Please try again or use a different URL.</div>
                                </>
                              ) : (
                                <>
                                  <div className="font-medium">Processing error</div>
                                  <div className="break-all">{project.error}</div>
                                </>
                              )}
                            </div>
                          </details>
                        )}
                      </div>
                    </td>
                    <td className="py-3">
                      <div className="flex gap-2">
                        <Link
                          href={`/projects/${project.id}`}
                          className="text-blue-600 hover:underline text-sm"
                        >
                          View
                        </Link>
                        {project.status === 'complete' && project.download_url && (
                          <a
                            href={`${process.env.NEXT_PUBLIC_API_URL}/jobs/${project.job_id}/preview`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-green-600 hover:underline text-sm"
                          >
                            Preview
                          </a>
                        )}
                        {project.status === 'complete' && project.download_url && (
                          <a
                            href={`${process.env.NEXT_PUBLIC_API_URL}/jobs/${project.job_id}/download`}
                            download
                            className="text-purple-600 hover:underline text-sm"
                          >
                            Download
                          </a>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
} 