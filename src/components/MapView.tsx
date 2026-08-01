"use client";
import React from 'react';
import Map, { Marker } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { Hackathon } from '@/lib/mockData';
import { MapPin } from 'lucide-react';

export default function MapView({ hackathons }: { hackathons: Hackathon[] }) {
  const mapboxToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || "";

  return (
    <div style={{ width: '100%', height: '100%', borderRadius: 'var(--border-radius-lg)', overflow: 'hidden' }}>
      {mapboxToken ? (
        <Map
          mapboxAccessToken={mapboxToken}
          initialViewState={{
            longitude: -122.4,
            latitude: 37.8,
            zoom: 1.5
          }}
          mapStyle="mapbox://styles/mapbox/dark-v11"
        >
          {hackathons.map((h) => (
            h.location.latitude && h.location.longitude ? (
              <Marker key={h.id} longitude={h.location.longitude} latitude={h.location.latitude}>
                <div style={{ color: 'var(--color-peach-glow)' }}>
                  <MapPin size={24} fill="currentColor" color="#000" />
                </div>
              </Marker>
            ) : null
          ))}
        </Map>
      ) : (
        <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-alabaster-grey)', color: '#000', padding: '2rem', textAlign: 'center' }}>
          <p><strong>Mapbox Token Missing</strong><br/>Please configure <code>NEXT_PUBLIC_MAPBOX_TOKEN</code> in your .env file to view the interactive map.</p>
        </div>
      )}
    </div>
  );
}
