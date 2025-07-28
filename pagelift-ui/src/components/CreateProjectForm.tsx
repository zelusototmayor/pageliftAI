"use client";
import { useState } from "react";
import { createProject } from "@/lib/api";

interface Props {
  onSuccess?: () => void;
}

export default function CreateProjectForm({ onSuccess }: Props) {
  const [url, setUrl] = useState("");
  const [projectName, setProjectName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await createProject({ url, project_name: projectName });
      setUrl("");
      setProjectName("");
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || "Failed to create project");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mb-8 bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Create New Project</h2>
      <div className="mb-4">
        <label className="block mb-1 font-medium">Project Name</label>
        <input
          type="text"
          className="w-full border rounded px-3 py-2"
          value={projectName}
          onChange={(e) => setProjectName(e.target.value)}
          required
        />
      </div>
      <div className="mb-4">
        <label className="block mb-1 font-medium">Website URL</label>
        <input
          type="url"
          className="w-full border rounded px-3 py-2"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
        />
      </div>
      {error && <div className="text-red-600 mb-2">{error}</div>}
      <button
        type="submit"
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition disabled:opacity-50"
        disabled={loading}
      >
        {loading ? "Creating..." : "Create Project"}
      </button>
    </form>
  );
} 