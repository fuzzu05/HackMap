import { NextResponse } from 'next/server';
import { hackathonIndex } from '@/lib/algolia';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.get('q');

  if (!query) {
    return NextResponse.json({ error: 'Missing query parameter' }, { status: 400 });
  }

  try {
    const { hits } = await hackathonIndex.search(query, {
      hitsPerPage: 10,
    });

    return NextResponse.json({ results: hits }, { status: 200 });
  } catch (error) {
    console.error('Error performing search:', error);
    // Return mock results if Algolia isn't fully configured by Fuzail yet
    return NextResponse.json({ 
      error: 'Algolia search failed, returning mock data',
      results: [
        { id: '1', name: `Mock Result for "${query}"`, type: 'mock' }
      ]
    }, { status: 500 });
  }
}
