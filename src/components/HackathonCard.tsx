import React, { useState } from 'react';
import { Hackathon } from '@/lib/mockData';
import styles from './HackathonCard.module.css';
import { Calendar, MapPin, Clock, Heart } from 'lucide-react';

export default function HackathonCard({ hackathon, userId }: { hackathon: Hackathon, userId?: string }) {
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [loading, setLoading] = useState(false);

  const toggleBookmark = async (e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    if (!userId) {
        alert("Please login to save hackathons!");
        return;
    }
    setLoading(true);
    try {
        const action = isBookmarked ? 'remove' : 'save';
        await fetch('/api/bookmarks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ userId, hackathonId: hackathon.id, action })
        });
        setIsBookmarked(!isBookmarked);
    } catch (error) {
        console.error('Failed to toggle bookmark', error);
    } finally {
        setLoading(false);
    }
  };
  const startDate = new Date(hackathon.dates.hackathonStart).toLocaleDateString();
  const endDate = new Date(hackathon.dates.hackathonEnd).toLocaleDateString();
  const locationStr = hackathon.mode === 'ONLINE' ? 'Online' : `${hackathon.location.city}, ${hackathon.location.country}`;

  return (
    <a href={(hackathon as any).sourceUrl || '#'} target="_blank" rel="noreferrer" className={styles.card} style={{ textDecoration: 'none' }}>
      <div 
        className={styles.image} 
        style={{ backgroundImage: `url(${hackathon.imageUrl || 'https://via.placeholder.com/800x400'})` }}
      />
      <div className={styles.content}>
        <div className={styles.header}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className={styles.formatBadge}>{hackathon.mode}</span>
            <button 
              onClick={toggleBookmark} 
              disabled={loading}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: isBookmarked ? '#ef4444' : 'var(--color-muted-sage)' }}
            >
              <Heart size={20} fill={isBookmarked ? '#ef4444' : 'none'} />
            </button>
          </div>
          <h3 className={styles.title}>{hackathon.title}</h3>
          <p className={styles.organizer}>{hackathon.tagline}</p>
        </div>
        
        <div className={styles.details}>
          <div className={styles.detailItem}>
            <Calendar size={16} />
            <span>{startDate} - {endDate}</span>
          </div>
          <div className={styles.detailItem}>
            <MapPin size={16} />
            <span>{locationStr}</span>
          </div>
          <div className={styles.detailItem}>
            <Clock size={16} />
            <span>{hackathon.status}</span>
          </div>
        </div>

        <div className={styles.techStack}>
          {hackathon.techStack.map(tech => (
            <span key={tech} className={styles.techBadge}>{tech}</span>
          ))}
        </div>
      </div>
    </a>
  );
}
