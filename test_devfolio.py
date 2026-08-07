import urllib.request, re, json
req = urllib.request.Request('https://devfolio.co/hackathons', headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        match = re.search(r'"buildId":"([^"]+)"', html)
        if match:
            build_id = match.group(1)
            print('Build ID:', build_id)
            # Test fetching JSON
            json_url = f'https://devfolio.co/_next/data/{build_id}/hackathons.json'
            req2 = urllib.request.Request(json_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req2) as resp2:
                data = json.loads(resp2.read())
                print('Keys:', data['pageProps'].keys())
                print('Hackathons count:', len(data['pageProps']['hackathons']))
                print('Example:', json.dumps(data['pageProps']['hackathons'][0], indent=2)[:500])
        else:
            print('No build ID found')
except Exception as e:
    print('Error:', e)
