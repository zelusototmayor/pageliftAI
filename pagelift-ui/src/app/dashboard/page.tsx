"use client";
import Link from "next/link";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { getProjects, Project } from "@/lib/api";
import CreateProjectForm from "@/components/CreateProjectForm";

export default function DashboardPage() {
  const queryClient = useQueryClient();
  const { data: projects, isLoading, error } = useQuery<Project[]>({
    queryKey: ["projects"],
    queryFn: getProjects,
  });

  return (
    <div className="max-w-2xl mx-auto py-10">
      <h1 className="text-3xl font-bold mb-6">Projects Dashboard</h1>
      <CreateProjectForm onSuccess={() => queryClient.invalidateQueries({ queryKey: ["projects"] })} />
      <div className="bg-white shadow rounded-lg p-6">
        {isLoading && <div className="text-gray-500">Loading projects...</div>}
        {error && <div className="text-red-600">Error loading projects.</div>}
        {projects && (
          <table className="w-full text-left">
            <thead>
              <tr>
                <th className="py-2">Project Name</th>
                <th className="py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((project) => (
                <tr key={project.id} className="border-t">
                  <td className="py-2">{project.name}</td>
                  <td className="py-2">
                    <Link
                      href={`/projects/${project.id}`}
                      className="text-blue-600 hover:underline"
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
} 