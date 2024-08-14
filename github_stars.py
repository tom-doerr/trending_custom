#!/usr/bin/env python3

import requests
import json
import csv
import argparse
from collections import defaultdict

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
        print(f"Error: Unable to fetch data for {username}. {e}")
        return []
    
    stars = response.json()
    
    if not stars:
        print(f"No starred repositories found for {username}")
        return []
    
    return stars

def get_top_accounts(csv_file, n):
    accounts = []
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        accounts = [(row[0], int(row[1])) for row in reader]
    
    return sorted(accounts, key=lambda x: x[1], reverse=True)[:n]

def process_accounts(config_file, top_n):
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    count = config['count']
    csv_file = 'github_following.csv'
    top_accounts = get_top_accounts(csv_file, top_n)
    
    all_stars = []
    for username, _ in top_accounts:
        stars = get_newest_stars(username, count)
        all_stars.extend([(star, username) for star in stars])
    
    return all_stars

def create_ranking(all_stars):
    repo_counts = defaultdict(list)
    for star, username in all_stars:
        repo_key = f"{star['owner']['login']}/{star['name']}"
        repo_counts[repo_key].append(username)
    
    sorted_repos = sorted(repo_counts.items(), key=lambda x: len(x[1]), reverse=True)
    
    print("Repository Ranking:")
    for i, (repo, usernames) in enumerate(sorted_repos, 1):
        print(f"{i}. {repo} - Starred by {len(usernames)} account(s): {', '.join(usernames)}")
        repo_url = next(star['html_url'] for star, _ in all_stars if f"{star['owner']['login']}/{star['name']}" == repo)
        print(f"   URL: {repo_url}")
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch GitHub stars for top accounts")
    parser.add_argument("--top", type=int, default=100, help="Number of top accounts to consider (default: 100)")
    args = parser.parse_args()

    config_file = 'config.json'
    all_stars = process_accounts(config_file, args.top)
    create_ranking(all_stars)
