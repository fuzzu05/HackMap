import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.get('q');

  if (!query) {
    return NextResponse.json({ error: 'Missing query parameter' }, { status: 400 });
  }

  try {
    // TODO: Implement actual Algolia search here using algoliasearch client
    // For Phase 1, we return a mock placeholder indicating the architecture is set up.
    
    const mockResults = [
      { id: '1', title: `Result for "${query}"`, type: 'mock' }
    ];

    return NextResponse.json({ results: mockResults }, { status: 200 });
  } catch (error) {
    console.error('Error performing search:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
