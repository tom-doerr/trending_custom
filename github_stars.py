#!/usr/bin/env python3

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
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error: Unable to fetch data. {e}")
        return
    
    stars = response.json()
    
    if not stars:
        print(f"No starred repositories found for {username}")
        return
    
    print(f"Newest {len(stars)} stars for {username}:")
    for star in stars:
        repo_name = star['name']
        repo_url = star['html_url']
        owner = star['owner']['login']
        # The 'starred_at' information is not directly available in the API response
        # We'll use the 'updated_at' field of the repository as an approximation
        updated_at = datetime.strptime(star['updated_at'], "%Y-%m-%dT%H:%M:%SZ")
        print(f"- {repo_name} (by {owner})")
        print(f"  URL: {repo_url}")
        print(f"  Last updated: {updated_at}")
        print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python github_stars.py <username> [count]")
        sys.exit(1)
    
    username = sys.argv[1]
    try:
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    except ValueError:
        print("Error: Count must be an integer")
        sys.exit(1)
    
    get_newest_stars(username, count)
