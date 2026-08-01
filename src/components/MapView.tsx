"use client";
import React from 'react';
import dynamic from 'next/dynamic';
import { Hackathon } from '@/lib/mockData';

// Leaflet requires window, so we must dynamically import it with ssr: false
const MapComponent = dynamic(() => import('./MapComponent'), {
  ssr: false,
  loading: () => (
    <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-alabaster-grey)' }}>
      <p>Loading Map...</p>
    </div>
  )
});

export default function MapView({ hackathons }: { hackathons: Hackathon[] }) {
  return (
    <div style={{ width: '100%', height: '100%', borderRadius: 'var(--border-radius-lg)', overflow: 'hidden' }}>
      <MapComponent hackathons={hackathons} />
    </div>
  );
}
