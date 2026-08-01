import { NextResponse } from 'next/server';
import { db } from '@/lib/firebase/config';
import { doc, getDoc, setDoc, deleteDoc, collection, getDocs } from 'firebase/firestore';

export async function POST(request: Request) {
  try {
    const { userId, hackathonId, action } = await request.json();

    if (!userId || !hackathonId || !action) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }

    const bookmarkRef = doc(db, 'users', userId, 'bookmarks', hackathonId);

    if (action === 'save') {
      await setDoc(bookmarkRef, {
        hackathonId,
        savedAt: new Date().toISOString()
      });
      return NextResponse.json({ status: 'saved' }, { status: 200 });
    } else if (action === 'remove') {
      await deleteDoc(bookmarkRef);
      return NextResponse.json({ status: 'removed' }, { status: 200 });
    } else {
      return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('Error handling bookmark:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const userId = searchParams.get('userId');

  if (!userId) {
    return NextResponse.json({ error: 'Missing userId' }, { status: 400 });
  }

  try {
    const bookmarksRef = collection(db, 'users', userId, 'bookmarks');
    const snapshot = await getDocs(bookmarksRef);
    const bookmarks = snapshot.docs.map(doc => doc.id);
    
    return NextResponse.json({ bookmarks }, { status: 200 });
  } catch (error) {
    console.error('Error fetching bookmarks:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
