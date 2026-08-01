'use client';

import { useEffect, useState } from 'react';
import { auth } from '@/lib/firebase/config';
import { logout } from '@/lib/firebase/auth';
import { useRouter } from 'next/navigation';
import { onAuthStateChanged, User } from 'firebase/auth';

export default function Dashboard() {
  const [user, setUser] = useState<User | null>(null);
  const router = useRouter();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (!currentUser) {
        router.push('/login');
      } else {
        setUser(currentUser);
      }
    });
    return () => unsubscribe();
  }, [router]);

  if (!user) return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-8 h-8 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
    </div>
  );

  return (
    <div className="p-8 max-w-4xl mx-auto mt-10 bg-white rounded-xl shadow-sm border border-gray-100">
      <h1 className="text-3xl font-bold mb-6 text-gray-900">HackMap Dashboard</h1>
      <div className="bg-gray-50 p-6 rounded-lg mb-6 border border-gray-200">
        <h2 className="text-xl font-semibold mb-2">Profile Information</h2>
        <p className="text-gray-700"><strong>Email:</strong> {user.email}</p>
        <p className="text-gray-700"><strong>User ID:</strong> {user.uid}</p>
      </div>
      <button 
        onClick={() => logout()} 
        className="bg-red-500 hover:bg-red-600 text-white font-semibold px-6 py-2 rounded-md transition"
      >
        Logout
      </button>
    </div>
  );
}
