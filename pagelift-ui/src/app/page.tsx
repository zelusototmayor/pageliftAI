import Image from "next/image";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-50">
      <h1 className="text-4xl font-bold mb-6">Welcome to PageLift AI</h1>
      <p className="mb-8 text-lg text-gray-600">Rebuild any website with AI-powered modern design.</p>
      <a
        href="/dashboard"
        className="px-6 py-3 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-700 transition text-lg font-semibold"
      >
        Try now
      </a>
    </main>
  );
}
