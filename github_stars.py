#!/usr/bin/env python3

import requests
import json
import csv
import argparse
import os
import subprocess
from collections import defaultdict
from requests.auth import HTTPBasicAuth
from tqdm import tqdm
from colorama import init, Fore, Style
from dotenv import load_dotenv

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()

def load_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    config['github_token'] = os.getenv('GITHUB_TOKEN')
    return config

def load_ignored_repos():
    try:
        with open('ignored_repos.txt', 'r') as f:
            return set(line.strip() for line in f if line.strip() and not line.startswith('#'))
    except FileNotFoundError:
        print(f"{Fore.YELLOW}Warning: ignored_repos.txt not found. No repositories will be ignored.")
        return set()

def add_to_ignored_repos(repo):
    with open('ignored_repos.txt', 'a') as f:
        f.write(f"{repo}\n")

def get_newest_stars(username, count, token):
    print(f"\nFetching stars for user: {username}")
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

def process_accounts(config_file, top_n, token, args):
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    count = max(config['count'], args.final_ranking)
    csv_file = 'github_following.csv'
    top_accounts = get_top_accounts(csv_file, top_n)
    
    ignored_repos = load_ignored_repos()
    
    all_stars = []
    total_stars_considered = 0
    with tqdm(total=len(top_accounts), desc="Processing accounts", position=0, leave=True) as pbar:
        for username, _ in top_accounts:
            stars = get_newest_stars(username, count, token)
            filtered_stars = [star for star in stars if f"{star['owner']['login']}/{star['name']}" not in ignored_repos]
            all_stars.extend([(star, username) for star in filtered_stars])
            total_stars_considered += len(stars)
            
            # Update progress bar
            pbar.update(1)
            pbar.set_description(f"Processing accounts ({pbar.n}/{pbar.total})")
    
    return all_stars, total_stars_considered

def create_ranking(all_stars, top_repos):
    repo_counts = defaultdict(list)
    for star, username in all_stars:
        repo_key = f"{star['owner']['login']}/{star['name']}"
        repo_counts[repo_key].append(username)
    
    sorted_repos = sorted(repo_counts.items(), key=lambda x: len(x[1]), reverse=True)[:top_repos]
    return sorted_repos

def display_ranking(sorted_repos, interactive=False):
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.YELLOW}Repository Ranking (Most Popular at Top)")
    print(f"{Fore.CYAN}{'=' * 60}\n")
    
    for i, (repo, usernames) in enumerate(sorted_repos, 1):
        print(f"{Fore.MAGENTA}{i:3}. {Fore.GREEN}{repo}")
        repo_url = next(star['html_url'] for star, _ in all_stars if f"{star['owner']['login']}/{star['name']}" == repo)
        print(f"    {Fore.CYAN}URL: {Fore.BLUE}{repo_url}")
        print(f"    {Fore.CYAN}Starred by {Fore.YELLOW}{len(usernames)} {Fore.CYAN}account(s):")
        print(f"    {Fore.YELLOW}{', '.join(usernames)}")
        print()
        
        if interactive:
            input("Press Enter to continue...")
            try:
                subprocess.run(['brave', repo_url], check=True)
            except subprocess.CalledProcessError:
                print(f"{Fore.RED}Error: Unable to open Brave browser. Make sure it's installed and accessible from the command line.")
            except FileNotFoundError:
                print(f"{Fore.RED}Error: Brave browser not found. Make sure it's installed and accessible from the command line.")
            add_to_ignored_repos(repo)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch GitHub stars for top accounts")
    parser.add_argument("--top-accounts", type=int, default=100, help="Number of top accounts to consider (default: 100)")
    parser.add_argument("--top-repos", type=int, default=50, help="Number of top repositories to display (default: 50)")
    parser.add_argument("--final-ranking", type=int, default=50, help="Number of items to show in the final ranking (default: 50)")
    parser.add_argument("--no-interactive", action="store_true", help="Disable interactive mode")
    args = parser.parse_args()

    config = load_config()
    token = config.get('github_token')
    
    config_file = 'config.json'
    
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.YELLOW}GitHub Stars Analysis")
    print(f"{Fore.CYAN}{'=' * 60}\n")
    
    ignored_repos = load_ignored_repos()
    if ignored_repos:
        print(f"{Fore.YELLOW}Ignoring {len(ignored_repos)} repositories listed in ignored_repos.txt")
    
    print(f"{Fore.GREEN}Processing top {Fore.YELLOW}{args.top_accounts} {Fore.GREEN}accounts...")
    all_stars, total_stars_considered = process_accounts(config_file, args.top_accounts, token, args)
    
    print(f"\n{Fore.CYAN}Total stars considered: {Fore.GREEN}{total_stars_considered}")
    
    sorted_repos = create_ranking(all_stars, args.final_ranking)
    
    display_ranking(sorted_repos, interactive=not args.no_interactive)
    
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.YELLOW}Analysis Complete")
    print(f"{Fore.CYAN}Total stars considered: {Fore.GREEN}{total_stars_considered}")
    print(f"{Fore.CYAN}{'=' * 60}")
