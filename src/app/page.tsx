"use client";

import React, { useState, useEffect, useCallback } from 'react';
import FilterSidebar from '@/components/FilterSidebar';
import HackathonCard from '@/components/HackathonCard';
import MapView from '@/components/MapView';
import { Hackathon } from '@/lib/mockData';
import styles from './page.module.css';

export default function DiscoveryPage() {
  const [filters, setFilters] = useState({});
  const [hackathons, setHackathons] = useState<Hackathon[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchHackathons() {
      setLoading(true);
      try {
        let url = '/api/search?q=';
        const modes = (filters as any).modes;
        if (modes && modes.length > 0) {
          url += '&modes=' + encodeURIComponent(modes.join(','));
        }
        
        const duration = (filters as any).duration;
        if (duration) {
          url += '&duration=' + duration;
        }
        
        const res = await fetch(url);
        const data = await res.json();

        // Zubaida's API gracefully falls back to mock results on failure
        if (!res.ok) {
          console.warn(data.error);
        }

        setHackathons(data.results || []);
        setError(null);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchHackathons();
  }, [filters]);

  const handleFilterChange = useCallback((newFilters: any) => {
    setFilters(newFilters);
  }, []);

  return (
    <main className={styles.container}>
      <FilterSidebar onFilterChange={handleFilterChange} />

      <div className={styles.mainContent}>
        <section className={styles.listSection}>
          <div className={styles.header}>
            <h1>Discover Hackathons</h1>
            <p>Find your next challenge globally.</p>
          </div>

          {loading ? (
            <div style={{ padding: '2rem', textAlign: 'center' }}>Loading hackathons...</div>
          ) : hackathons.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center' }}>No hackathons found.</div>
          ) : (
            hackathons.map((hackathon) => (
              <HackathonCard key={hackathon.id} hackathon={hackathon} />
            ))
          )}
        </section>

        <section className={styles.mapSection}>
          <MapView hackathons={hackathons} />
        </section>
      </div>
    </main>
  );
}
