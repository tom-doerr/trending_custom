#!/usr/bin/env python3

import requests
import json
import csv
import argparse
from collections import defaultdict
from requests.auth import HTTPBasicAuth
from tqdm import tqdm

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def get_newest_stars(username, count, token):
    url = f"https://api.github.com/users/{username}/starred"
    params = {
        "sort": "created",
        "direction": "desc",
        "per_page": count
    }
    headers = {'Authorization': f'token {token}'} if token else {}
    
    try:
        response = requests.get(url, params=params, headers=headers)
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

def process_accounts(config_file, top_n, token):
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    count = config['count']
    csv_file = 'github_following.csv'
    top_accounts = get_top_accounts(csv_file, top_n)
    
    all_stars = []
    with tqdm(total=len(top_accounts), desc="Processing accounts") as pbar:
        for username, _ in top_accounts:
            stars = get_newest_stars(username, count, token)
            all_stars.extend([(star, username) for star in stars])
            pbar.update(1)
    
    return all_stars

def create_ranking(all_stars, top_repos):
    repo_counts = defaultdict(list)
    for star, username in all_stars:
        repo_key = f"{star['owner']['login']}/{star['name']}"
        repo_counts[repo_key].append(username)
    
    sorted_repos = sorted(repo_counts.items(), key=lambda x: len(x[1]), reverse=True)[:top_repos]
    
    print("Repository Ranking:")
    for i, (repo, usernames) in enumerate(reversed(sorted_repos), 1):
        rank = top_repos - i + 1
        print(f"{rank}. {repo} - Starred by {len(usernames)} account(s): {', '.join(usernames)}")
        repo_url = next(star['html_url'] for star, _ in all_stars if f"{star['owner']['login']}/{star['name']}" == repo)
        print(f"   URL: {repo_url}")
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch GitHub stars for top accounts")
    parser.add_argument("--top-accounts", type=int, default=100, help="Number of top accounts to consider (default: 100)")
    parser.add_argument("--top-repos", type=int, default=40, help="Number of top repositories to display (default: 40)")
    args = parser.parse_args()

    config = load_config()
    token = config.get('github_token')
    
    config_file = 'config.json'
    all_stars = process_accounts(config_file, args.top_accounts, token)
    create_ranking(all_stars, args.top_repos)
