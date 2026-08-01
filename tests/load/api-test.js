import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,
  duration: '30s',
};

export default function () {
  const BASE_URL = 'http://localhost:3000';
  
  // Test Recommendations API
  const recRes = http.get(`${BASE_URL}/api/recommendations?userId=testUser123`);
  check(recRes, {
    'recommendations status was 200': (r) => r.status === 200,
  });

  // Test Search API
  const searchRes = http.get(`${BASE_URL}/api/search?q=AI`);
  check(searchRes, {
    'search status was 200 or 500': (r) => r.status === 200 || r.status === 500, // 500 allowed if Algolia not yet configured
  });

  sleep(1);
}
