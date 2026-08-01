import Link from 'next/link';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8 sm:p-20 font-[family-name:var(--font-geist-sans)] bg-gray-50">
      <main className="flex flex-col gap-8 row-start-2 items-center text-center max-w-2xl">
        <h1 className="text-5xl font-extrabold tracking-tight text-gray-900">
          Welcome to <span className="text-blue-600">HackMap</span>
        </h1>
        <p className="text-lg text-gray-600">
          The ultimate platform to discover, filter, and track hackathons globally.
        </p>
        
        <div className="flex gap-4 items-center flex-col sm:flex-row mt-8">
          <Link
            className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-blue-600 text-white gap-2 hover:bg-blue-700 text-sm sm:text-base h-12 px-8 font-semibold shadow-sm"
            href="/login"
          >
            Get Started
          </Link>
          <Link
            className="rounded-full border border-solid border-gray-300 transition-colors flex items-center justify-center bg-white text-gray-900 hover:bg-gray-100 text-sm sm:text-base h-12 px-8 font-semibold"
            href="/dashboard"
          >
            Go to Dashboard
          </Link>
        </div>
      </main>
    </div>
  );
}
