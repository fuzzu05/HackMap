export interface Hackathon {
  id: string;
  name: string;
  organizer: string;
  date: string;
  duration: number; // in hours
  location: string;
  region: string;
  format: "In-Person" | "Online" | "Hybrid";
  techStack: string[];
  imageUrl: string;
  coordinates: {
    latitude: number;
    longitude: number;
  };
}

export const mockHackathons: Hackathon[] = [
  {
    id: "1",
    name: "Global AI Hack 2026",
    organizer: "AI Innovators",
    date: "Aug 15 - Aug 17, 2026",
    duration: 48,
    location: "San Francisco, CA",
    region: "North America",
    format: "In-Person",
    techStack: ["Python", "TensorFlow", "React"],
    imageUrl: "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800&q=80",
    coordinates: { latitude: 37.7749, longitude: -122.4194 }
  },
  {
    id: "2",
    name: "Web3 BuilderFest",
    organizer: "Decentralized Inc",
    date: "Sep 01 - Sep 03, 2026",
    duration: 72,
    location: "Online",
    region: "Global",
    format: "Online",
    techStack: ["Solidity", "Next.js", "TypeScript"],
    imageUrl: "https://images.unsplash.com/photo-1639322537228-f710d846310a?w=800&q=80",
    coordinates: { latitude: 0, longitude: 0 }
  },
  {
    id: "3",
    name: "London Fintech Hackathon",
    organizer: "FinBank UK",
    date: "Oct 10 - Oct 12, 2026",
    duration: 48,
    location: "London, UK",
    region: "Europe",
    format: "Hybrid",
    techStack: ["Java", "Spring Boot", "React"],
    imageUrl: "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800&q=80",
    coordinates: { latitude: 51.5074, longitude: -0.1278 }
  }
];
