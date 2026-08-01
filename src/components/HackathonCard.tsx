import React from 'react';
import { Hackathon } from '@/lib/mockData';
import styles from './HackathonCard.module.css';
import { Calendar, MapPin, Clock } from 'lucide-react';

export default function HackathonCard({ hackathon }: { hackathon: Hackathon }) {
  return (
    <div className={styles.card}>
      <div 
        className={styles.image} 
        style={{ backgroundImage: `url(${hackathon.imageUrl})` }}
      />
      <div className={styles.content}>
        <div className={styles.header}>
          <span className={styles.formatBadge}>{hackathon.format}</span>
          <h3 className={styles.title}>{hackathon.name}</h3>
          <p className={styles.organizer}>by {hackathon.organizer}</p>
        </div>
        
        <div className={styles.details}>
          <div className={styles.detailItem}>
            <Calendar size={16} />
            <span>{hackathon.date}</span>
          </div>
          <div className={styles.detailItem}>
            <MapPin size={16} />
            <span>{hackathon.location}</span>
          </div>
          <div className={styles.detailItem}>
            <Clock size={16} />
            <span>{hackathon.duration} Hours</span>
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
