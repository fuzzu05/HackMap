import hashlib
import time
from typing import Tuple
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import logging

logger = logging.getLogger(__name__)

# Global cache to avoid hitting Nominatim repeatedly for the same city
_GEOCODE_CACHE = {}

def geocode_and_jitter_offline(city: str, country: str, hackathon_id: str) -> Tuple[float, float]:
    """
    Geocodes a city/country to get base coordinates, then applies a small jitter
    so multiple offline hackathons in the same city don't perfectly overlap on the map.
    Returns (lat, lng) or (None, None) if geocoding fails.
    """
    if not city:
        return None, None
        
    query = f"{city}, {country}" if country else city
    base_coords = None
    
    if query in _GEOCODE_CACHE:
        base_coords = _GEOCODE_CACHE[query]
    else:
        try:
            # Nominatim requires a custom user agent
            geolocator = Nominatim(user_agent="HackMap_DataPipeline_v1")
            
            # Sleep briefly to respect Nominatim's 1 req/sec policy
            time.sleep(1.1)
            
            location = geolocator.geocode(query, timeout=5)
            if location:
                base_coords = (location.latitude, location.longitude)
                _GEOCODE_CACHE[query] = base_coords
                logger.info("Geocoded '%s' to %s", query, base_coords)
            else:
                _GEOCODE_CACHE[query] = None
                logger.warning("Could not geocode '%s'", query)
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            logger.error("Geocoding service failed for '%s': %s", query, e)
            return None, None
            
    if not base_coords:
        return None, None
        
    # Apply city-level jitter (~5km max offset)
    # 0.05 degrees of lat/long is roughly 5km
    h = hashlib.sha256(hackathon_id.encode("utf-8")).hexdigest()
    
    # Map hash to [-0.05, 0.05]
    val1 = (int(h[:8], 16) / 0xFFFFFFFF) * 0.10 - 0.05
    val2 = (int(h[8:16], 16) / 0xFFFFFFFF) * 0.10 - 0.05
    
    jittered_lat = base_coords[0] + val1
    jittered_lng = base_coords[1] + val2
    
    return round(jittered_lat, 5), round(jittered_lng, 5)
