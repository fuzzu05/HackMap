"use client";
import React, { useEffect, useState } from 'react';

// Dashboard component isolated to avoid merge conflicts with Fuzail's page.tsx
export default function DashboardView({ userId }: { userId: string }) {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchRecs() {
      try {
        const res = await fetch(`/api/recommendations?userId=${userId}`);
        const data = await res.json();
        
        // Ensure recommendations is always an array to map over
        if (data.recommendations && Array.isArray(data.recommendations)) {
            setRecommendations(data.recommendations);
        } else {
            setRecommendations([]);
        }
      } catch (err) {
        console.error('Failed to fetch recommendations:', err);
      } finally {
        setLoading(false);
      }
    }
    
    if (userId) {
        fetchRecs();
    }
  }, [userId]);

  return (
    <div style={{ padding: 'var(--spacing-xl)', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '2rem', marginBottom: 'var(--spacing-lg)' }}>Your Dashboard</h1>
      
      <section style={{ marginBottom: 'var(--spacing-xl)' }}>
        <h2 style={{ fontSize: '1.5rem', marginBottom: 'var(--spacing-md)', color: 'var(--color-peach-glow)' }}>
          Recommended For You
        </h2>
        
        {loading ? (
          <p>Loading personalized recommendations...</p>
        ) : recommendations.length === 0 ? (
          <p>No recommendations yet. Participate in more hackathons to train your algorithm!</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 'var(--spacing-lg)' }}>
             {/* The API currently returns RecommendationDocuments from Firestore. We iterate over their rankedHackathons */}
             {recommendations.map((recDoc, index) => (
                recDoc.rankedHackathons?.map((rec: any) => (
                    <div key={rec.hackathonId} style={{ padding: '1rem', border: '1px solid var(--color-muted-sage)', borderRadius: 'var(--border-radius-md)' }}>
                        <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>Match Score: {(rec.score * 100).toFixed(0)}%</h3>
                        <p style={{ fontSize: '0.9rem', opacity: 0.8 }}><strong>Hackathon ID:</strong> {rec.hackathonId}</p>
                        
                        {rec.matchReasons && rec.matchReasons.length > 0 && (
                            <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem', fontSize: '0.85rem' }}>
                                {rec.matchReasons.map((reason: string, i: number) => (
                                    <li key={i}>{reason}</li>
                                ))}
                            </ul>
                        )}
                    </div>
                ))
             ))}
          </div>
        )}
      </section>

      <section>
        <h2 style={{ fontSize: '1.5rem', marginBottom: 'var(--spacing-md)', color: 'var(--color-peach-glow)' }}>
          Saved Bookmarks
        </h2>
        <div style={{ padding: '2rem', textAlign: 'center', border: '1px dashed var(--color-muted-sage)', borderRadius: 'var(--border-radius-lg)' }}>
            <p>Your bookmarked hackathons will appear here.</p>
        </div>
      </section>
    </div>
  );
}
