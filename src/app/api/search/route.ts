import { NextResponse } from 'next/server';
import { hackathonIndex } from '@/lib/algolia';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.get('q') || '';
  const modesStr = searchParams.get('modes');

  try {
    const searchOptions: any = { hitsPerPage: 100 };
    
    if (modesStr) {
      const modes = modesStr.split(',');
      searchOptions.filters = modes.map(m => `mode:${m}`).join(' OR ');
    }

    const { hits } = await hackathonIndex.search(query, searchOptions);

    return NextResponse.json({ results: hits }, { status: 200 });
  } catch (error) {
    console.error('Error performing search:', error);
    // Return robust mock data adhering to the JSON contract if Algolia fails
    return NextResponse.json({
      error: 'Algolia search failed, returning mock data',
      results: [
        {
          id: 'mock-global-ai-hackathon',
          title: `Global AI Hackathon 2026 (Mock for "${query}")`,
          tagline: 'Build the future of agentic AI',
          imageUrl: 'https://via.placeholder.com/800x400?text=Hackathon+Banner',
          mode: 'HYBRID',
          location: { city: 'San Francisco', country: 'USA', latitude: 37.7749, longitude: -122.4194, isOnline: true },
          dates: {
            registrationOpen: '2026-08-01T00:00:00Z',
            registrationClose: '2026-09-01T00:00:00Z',
            hackathonStart: '2026-09-05T00:00:00Z',
            hackathonEnd: '2026-09-07T00:00:00Z'
          },
          prizes: { totalPoolUsd: 50000, currency: 'USD' },
          tags: ['AI', 'Web3', 'Beginner Friendly'],
          techStack: ['Python', 'Next.js'],
          eligibility: 'Global, Open to all',
          status: 'UPCOMING'
        }
      ]
    }, { status: 500 });
  }
}
