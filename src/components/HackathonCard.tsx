import React from 'react';
import { Hackathon } from '@/lib/mockData';
import styles from './HackathonCard.module.css';
import { Calendar, MapPin, Clock } from 'lucide-react';

export default function HackathonCard({ hackathon }: { hackathon: Hackathon }) {
  const startDate = new Date(hackathon.dates.hackathonStart).toLocaleDateString();
  const endDate = new Date(hackathon.dates.hackathonEnd).toLocaleDateString();
  const locationStr = hackathon.mode === 'ONLINE' ? 'Online' : `${hackathon.location.city}, ${hackathon.location.country}`;

  return (
    <div className={styles.card}>
      <div 
        className={styles.image} 
        style={{ backgroundImage: `url(${hackathon.imageUrl || 'https://via.placeholder.com/800x400'})` }}
      />
      <div className={styles.content}>
        <div className={styles.header}>
          <span className={styles.formatBadge}>{hackathon.mode}</span>
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
    </div>
  );
}
