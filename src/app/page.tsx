"use client";

import React, { useState } from 'react';
import FilterSidebar from '@/components/FilterSidebar';
import HackathonCard from '@/components/HackathonCard';
import MapView from '@/components/MapView';
import { mockHackathons } from '@/lib/mockData';
import styles from './page.module.css';

export default function DiscoveryPage() {
  const [filters, setFilters] = useState({});
  const [hackathons, setHackathons] = useState(mockHackathons);

  const handleFilterChange = (newFilters: any) => {
    setFilters(newFilters);
  };

  return (
    <main className={styles.container}>
      <FilterSidebar onFilterChange={handleFilterChange} />
      
      <div className={styles.mainContent}>
        <section className={styles.listSection}>
          <div className={styles.header}>
            <h1>Discover Hackathons</h1>
            <p>Find your next challenge globally.</p>
          </div>
          
          {hackathons.map((hackathon) => (
            <HackathonCard key={hackathon.id} hackathon={hackathon} />
          ))}
        </section>
        
        <section className={styles.mapSection}>
          <MapView hackathons={hackathons} />
        </section>
      </div>
    </main>
  );
}
