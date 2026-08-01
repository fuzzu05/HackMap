"use client";
import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { Hackathon } from '@/lib/mockData';

// Fix leaflet default icons in React
const icon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

export default function MapComponent({ hackathons }: { hackathons: Hackathon[] }) {
  return (
    <MapContainer 
      center={[37.8, -122.4]} 
      zoom={2} 
      scrollWheelZoom={true} 
      style={{ width: '100%', height: '100%' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {hackathons.map((h) => {
        if (h.mode === 'ONLINE') return null;
        
        let lat = h.location.latitude;
        let lng = h.location.longitude;
        
        if (!lat || !lng) {
          const cityCoords: Record<string, [number, number]> = {
            'San Francisco': [37.7749, -122.4194],
            'London': [51.5074, -0.1278],
            'Berlin': [52.5200, 13.4050],
            'Tokyo': [35.6762, 139.6503],
            'Bangalore': [12.9716, 77.5946]
          };
          if (h.location.city && cityCoords[h.location.city]) {
            [lat, lng] = cityCoords[h.location.city];
          }
        }
        
        if (!lat || !lng) return null;

        return (
          <Marker 
            key={h.id} 
            position={[lat, lng]} 
            icon={icon}
          >
            <Popup>
              <strong>{h.title}</strong><br />
              {h.location.city}, {h.location.country}
            </Popup>
          </Marker>
        );
      })}
    </MapContainer>
  );
}
