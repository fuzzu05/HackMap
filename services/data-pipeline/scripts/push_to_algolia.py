import json
import os
import sys
from algoliasearch.search_client import SearchClient

def main():
    dump_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'hackathons_dump.json')
    
    if not os.path.exists(dump_path):
        print(f"Error: {dump_path} not found.")
        sys.exit(1)
        
    app_id = os.environ.get('ALGOLIA_APP_ID')
    api_key = os.environ.get('ALGOLIA_ADMIN_KEY') or os.environ.get('ALGOLIA_WRITE_KEY')
    
    if not app_id or not api_key:
        print("Warning: ALGOLIA_APP_ID and ALGOLIA_ADMIN_KEY environment variables are required.")
        print("Skipping Algolia push. This is expected in non-production local runs.")
        sys.exit(0)
        
    client = SearchClient.create(app_id, api_key)
    index = client.init_index('hackathons')
    
    with open(dump_path, 'r', encoding='utf-8') as f:
        hackathons = json.load(f)
        
    # Algolia requires 'objectID' instead of 'id'
    algolia_records = []
    for h in hackathons:
        record = h.copy()
        record['objectID'] = record.pop('id')
        
        # Algolia geo-search expects _geoloc for lat/long
        if record.get('location') and record['location'].get('latitude') is not None and record['location'].get('longitude') is not None:
            record['_geoloc'] = {
                'lat': record['location']['latitude'],
                'lng': record['location']['longitude']
            }
            
        algolia_records.append(record)
        
    print(f"Pushing {len(algolia_records)} hackathons to Algolia...")
    try:
        # replace_all_objects guarantees stale data is removed!
        index.replace_all_objects(algolia_records)
        print("Successfully synced with Algolia!")
    except Exception as e:
        print(f"Error pushing to Algolia: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
