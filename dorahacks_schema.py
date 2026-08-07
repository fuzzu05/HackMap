import urllib.request, json
req = urllib.request.Request(
    'https://dorahacks.io/api/v1/hub/hackathons?page=1&page_size=1', 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept': 'application/json'},
    method='GET'
)
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        print(json.dumps(data['results'][0], indent=2))
except Exception as e:
    print('Error:', e)
