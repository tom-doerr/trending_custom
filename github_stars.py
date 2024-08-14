import requests
import sys
from datetime import datetime

def get_newest_stars(username, count=10):
    url = f"https://api.github.com/users/{username}/starred"
    params = {
        "sort": "created",
        "direction": "desc",
        "per_page": count
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")
        return
    
    stars = response.json()
    
    print(f"Newest {count} stars for {username}:")
    for star in stars:
        repo_name = star['name']
        repo_url = star['html_url']
        starred_at = datetime.strptime(star['starred_at'], "%Y-%m-%dT%H:%M:%SZ")
        print(f"- {repo_name}")
        print(f"  URL: {repo_url}")
        print(f"  Starred at: {starred_at}")
        print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python github_stars.py <username> [count]")
        sys.exit(1)
    
    username = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    get_newest_stars(username, count)
