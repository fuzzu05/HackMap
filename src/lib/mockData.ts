export interface Hackathon {
  id: string;
  title: string;
  tagline: string;
  imageUrl: string;
  mode: "ONLINE" | "IN_PERSON" | "HYBRID";
  location: {
    city: string;
    country: string;
    latitude: number;
    longitude: number;
    isOnline: boolean;
  };
  dates: {
    registrationOpen: string;
    registrationClose: string;
    hackathonStart: string;
    hackathonEnd: string;
  };
  prizes: {
    totalPoolUsd: number;
    currency: string;
  };
  tags: string[];
  techStack: string[];
  eligibility: string;
  status: "UPCOMING" | "ONGOING" | "ENDED";
}

export const mockHackathons: Hackathon[] = [];
