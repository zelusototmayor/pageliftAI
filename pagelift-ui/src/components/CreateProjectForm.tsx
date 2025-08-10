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

  function validateUrl(url: string): string | null {
    if (!url) return "URL is required";
    
    try {
      const urlObj = new URL(url);
      if (!['http:', 'https:'].includes(urlObj.protocol)) {
        return "URL must use http:// or https://";
      }
      if (!urlObj.hostname) {
        return "URL must include a valid domain name";
      }
      // Basic domain validation
      if (urlObj.hostname.includes('localhost') || urlObj.hostname.includes('127.0.0.1')) {
        return "Local URLs are not supported";
      }
      return null;
    } catch {
      return "Please enter a valid URL (e.g., https://example.com)";
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    
    // Validate URL before submission
    const urlError = validateUrl(url);
    if (urlError) {
      setError(urlError);
      return;
    }
    
    setLoading(true);
    try {
      await createProject({ url, project_name: projectName });
      setUrl("");
      setProjectName("");
      if (onSuccess) onSuccess();
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || err.message || "Failed to create project";
      setError(`Failed to create project: ${errorMessage}`);
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
          placeholder="https://example.com"
          required
        />
        <div className="text-sm text-gray-500 mt-1">
          Enter the website URL you want to convert (must start with http:// or https://)
        </div>
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