import urllib.request
import urllib.error
import json
import sys
from datetime import datetime

def check_requirements(filepath="requirements.txt"):
    try:
        with open(filepath, 'r') as f:
            lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    except FileNotFoundError:
        print("Error: requirements.txt not found.")
        sys.exit(1)

    checked_count = len(lines)
    missing_packages_count = 0
    missing_versions_count = 0
    valid_releases = []

    for line in lines:
        if '==' not in line:
            continue
            
        parts = line.split('==')
        pkg_name = parts[0].strip()
        version = parts[1].strip()
        
        url = f"https://pypi.org/pypi/{pkg_name}/json"
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                
            releases = data.get('releases', {})
            if version not in releases:
                missing_versions_count += 1
            else:
                files = releases[version]
                if files:
                    upload_time_str = files[0].get('upload_time')
                    if upload_time_str:
                        upload_time = datetime.strptime(upload_time_str.split('.')[0], "%Y-%m-%dT%H:%M:%S")
                        valid_releases.append({
                            'name': pkg_name,
                            'version': version,
                            'time': upload_time,
                            'year': upload_time.year
                        })
                        
        except urllib.error.HTTPError as e:
            if e.code == 404:
                missing_packages_count += 1

    print(f"1. {checked_count}")
    print(f"2. {missing_packages_count}")
    print(f"3. {missing_versions_count}")
    
    if valid_releases:
        oldest = min(valid_releases, key=lambda x: x['time'])
        print(f"4. {oldest['name']}=={oldest['version']} ({oldest['year']})")
    else:
        print("4. None found")

if __name__ == "__main__":
    check_requirements("requirements.txt")