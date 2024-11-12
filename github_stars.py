#!/usr/bin/env python3

import requests
import json
import csv
import argparse
import os
import subprocess
import concurrent.futures
from collections import defaultdict, Counter
from requests.auth import HTTPBasicAuth
from tqdm import tqdm
import matplotlib.pyplot as plt
from colorama import init, Fore, Style
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from datetime import datetime
import os
import pathlib
import json

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
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            if 'X-RateLimit-Remaining' in e.response.headers:
                remaining = e.response.headers['X-RateLimit-Remaining']
                reset_time = time.strftime('%H:%M:%S', time.localtime(int(e.response.headers['X-RateLimit-Reset'])))
                print(f"{Fore.RED}Error: Rate limit exceeded for {username}. "
                      f"Remaining requests: {remaining}. Reset time: {reset_time}")
            else:
                print(f"{Fore.RED}Error: Rate limit exceeded or authentication required for {username}. "
                      f"Check your GitHub token or wait a while.")
        else:
            print(f"{Fore.RED}Error: Unable to fetch data for {username}. HTTP {e.response.status_code}")
        return []
    except requests.RequestException as e:
        print(f"{Fore.RED}Error: Unable to fetch data for {username}. {e}")
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
        for row in reader:
            try:
                # Try old format (username, follower_count)
                accounts.append((row[0], int(row[1])))
            except ValueError:
                # New format (username, repo_list)
                # Use number of repos as the weight
                repo_count = len(row[1].split(','))
                accounts.append((row[0], repo_count))
    
    return sorted(accounts, key=lambda x: x[1], reverse=True)[:n]

def process_account(args):
    username, count, token, ignored_repos = args
    stars = get_newest_stars(username, count, token)
    filtered_stars = [star for star in stars if f"{star['owner']['login']}/{star['name']}" not in ignored_repos]
    return [(star, username) for star in filtered_stars], len(stars)

def process_accounts(config_file, top_n, token, args):
    count = args.stars_per_account
    top_accounts = get_top_accounts(args.csv_file, top_n)
    ignored_repos = load_ignored_repos()
    
    all_stars = []
    total_stars_considered = 0
    
    with tqdm(total=len(top_accounts), desc="Processing accounts", position=0, leave=True) as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as executor:
            # Prepare arguments for each account
            process_args = [(username, count, token, ignored_repos) for username, _ in top_accounts]
            
            # Submit all tasks
            future_to_username = {executor.submit(process_account, arg): arg[0] 
                                for arg in process_args}
            
            # Process completed tasks as they finish
            for future in concurrent.futures.as_completed(future_to_username):
                username = future_to_username[future]
                try:
                    stars, stars_count = future.result()
                    all_stars.extend(stars)
                    total_stars_considered += stars_count
                except Exception as e:
                    print(f"{Fore.RED}Error processing {username}: {e}")
                
                pbar.update(1)
                pbar.set_description(f"Processing accounts ({pbar.n}/{pbar.total})")
    
    return all_stars, total_stars_considered

def write_repo_data(sorted_repos, ignored_repos, timestamp=None):
    """Write repository data to timestamped files in both human and machine readable formats"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create reports directories if they don't exist
    reports_dir = pathlib.Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    data_dir = pathlib.Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Create the human-readable report file
    report_file = reports_dir / f"repo_report_{timestamp}.txt"
    
    with open(report_file, "w") as f:
        f.write(f"Repository Report - Generated at {timestamp}\n")
        f.write("=" * 80 + "\n\n")
        
        for repo, usernames in sorted_repos:
            is_ignored = repo in ignored_repos
            f.write(f"Repository: {repo}\n")
            f.write(f"Stars: {len(usernames)}\n")
            f.write(f"Status: {'Previously Displayed' if is_ignored else 'New'}\n")
            f.write("Starred by:\n")
            for username in usernames:
                f.write(f"  - {username}\n")
            f.write("\n" + "-" * 40 + "\n\n")
    
    # Create the machine-readable JSON file
    json_file = data_dir / f"repo_data_{timestamp}.json"
    
    json_data = {
        "generated_at": timestamp,
        "repositories": [
            {
                "name": repo,
                "stars_count": len(usernames),
                "status": "Previously Displayed" if repo in ignored_repos else "New",
                "starred_by": usernames
            }
            for repo, usernames in sorted_repos
        ]
    }
    
    with open(json_file, "w") as f:
        json.dump(json_data, f, indent=2)

def create_ranking(all_stars, top_repos, ignored_repos=None):
    if ignored_repos is None:
        ignored_repos = set()
    repo_counts = defaultdict(list)
    for star, username in all_stars:
        repo_key = f"{star['owner']['login']}/{star['name']}"
        if repo_key not in ignored_repos:
            repo_counts[repo_key].append(username)
    
    sorted_repos = sorted(repo_counts.items(), key=lambda x: len(x[1]), reverse=True)[:top_repos]
    return sorted_repos

def display_distribution(all_stars):
    star_counts = Counter(star['id'] for star, _ in all_stars)
    distribution = Counter(star_counts.values())
    
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.YELLOW}Star Distribution")
    print(f"{Fore.CYAN}{'=' * 60}\n")
    
    for stars, count in sorted(distribution.items()):
        print(f"{Fore.GREEN}{stars} star{'s' if stars > 1 else ''}: {Fore.YELLOW}{count} repo{'s' if count > 1 else ''}")
    
    # Create a bar plot of the distribution
    plt.figure(figsize=(10, 6))
    plt.bar(distribution.keys(), distribution.values(), color='skyblue')
    plt.title('Distribution of Stars Across Repositories')
    plt.xlabel('Number of Stars')
    plt.ylabel('Number of Repositories')
    plt.savefig('star_distribution.png')
    print(f"\n{Fore.CYAN}Distribution plot saved as 'star_distribution.png'")

def display_ranking(sorted_repos, interactive=False, all_stars=None, initial_ignored=None):
    # Create browser_opens.log if it doesn't exist
    if not os.path.exists('browser_opens.log'):
        with open('browser_opens.log', 'w') as f:
            f.write("# Log of repositories opened in browser\n")
            f.write("# Format: human_timestamp,unix_timestamp,repository_name\n")

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
            # Log before attempting to open browser
            now = datetime.now()
            human_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            unix_timestamp = int(now.timestamp())
            with open('browser_opens.log', 'a') as log:
                log.write(f"{human_timestamp},{unix_timestamp},{repo}\n")
            
            try:
                subprocess.run(['brave', repo_url], check=True)
            except subprocess.CalledProcessError:
                print(f"{Fore.RED}Error: Unable to open Brave browser. Make sure it's installed and accessible from the command line.")
            except FileNotFoundError:
                print(f"{Fore.RED}Error: Brave browser not found. Make sure it's installed and accessible from the command line.")
            add_to_ignored_repos(repo)
            
            # Check for changes to ignored repos after each repo
            if recheck_and_display(all_stars, args, initial_ignored):
                initial_ignored = load_ignored_repos()
                # Return to avoid continuing with stale data
                return

class IgnoreFileHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified_by_script = False
        
    def on_modified(self, event):
        if event.src_path.endswith('ignored_repos.txt'):
            if not self.last_modified_by_script:
                self.handle_external_modification()
            self.last_modified_by_script = False
            
    def handle_external_modification(self):
        # This will be called only for external modifications
        pass

def recheck_and_display(all_stars, args, initial_ignored):
    """Recheck ignored repos and redisplay if changed"""
    current_ignored = load_ignored_repos()
    
    # Count how many repos were added
    added = current_ignored - initial_ignored
    removed = initial_ignored - current_ignored
    
    # Only reload if more than one repo was added at once
    if len(added) > 1 or removed:
        # Set flag before modifying the file
        file_handler.last_modified_by_script = True
        
        from datetime import datetime
        now = datetime.now().strftime("%H:%M:%S")
        print(f"\n{Fore.YELLOW}[{now}] Multiple changes detected in ignored repositories!")
        
        if added:
            print(f"{Fore.GREEN}Added to ignore list ({len(added)} repos): {', '.join(added)}")
        if removed:
            print(f"{Fore.RED}Removed from ignore list ({len(removed)} repos): {', '.join(removed)}")
            
        print(f"{Fore.GREEN}Refiltering and displaying updated results...")
        sorted_repos = create_ranking(all_stars, args.final_ranking, current_ignored)
        display_distribution(all_stars)
        display_ranking(sorted_repos, interactive=not args.no_interactive, all_stars=all_stars, initial_ignored=current_ignored)
        return True
    return False

# Create a global file handler instance
file_handler = IgnoreFileHandler()

if __name__ == "__main__":
    # Set up the file system observer
    observer = Observer()
    observer.schedule(file_handler, path='.', recursive=False)
    observer.start()
    
    parser = argparse.ArgumentParser(description="Fetch GitHub stars for top accounts")
    parser.add_argument("--top-accounts", type=int, default=100, help="Number of top accounts to consider (default: 100)")
    parser.add_argument("--stars-per-account", type=int, default=50, help="Number of newest stars to consider per account (default: 50)")
    parser.add_argument("--final-ranking", type=int, default=100, help="Number of items to show in the final ranking (default: 100)")
    parser.add_argument("--no-interactive", action="store_true", help="Disable interactive mode")
    parser.add_argument("--csv-file", type=str, default='github_following.csv', 
                      help="Path to the GitHub following CSV file (default: github_following.csv)")
    parser.add_argument("--parallel", type=int, default=5,
                      help="Number of parallel requests (default: 5)")
    parser.add_argument("--save-top", type=int,
                      help="Save the top N repositories to a file")
    parser.add_argument("--output-file", type=str, default="top_repos.txt",
                      help="Filename to save top repositories (default: top_repos.txt)")
    args = parser.parse_args()

    config = load_config()
    token = config.get('github_token')
    
    config_file = 'config.json'
    
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.YELLOW}GitHub Stars Analysis")
    print(f"{Fore.CYAN}{'=' * 60}\n")
    
    initial_ignored = load_ignored_repos()
    if initial_ignored:
        print(f"{Fore.YELLOW}Ignoring {len(initial_ignored)} repositories listed in ignored_repos.txt")
    
    print(f"{Fore.GREEN}Processing top {Fore.YELLOW}{args.top_accounts} {Fore.GREEN}accounts...")
    print(f"{Fore.GREEN}Considering {Fore.YELLOW}{args.stars_per_account} {Fore.GREEN}newest stars per account...")
    all_stars, total_stars_considered = process_accounts(config_file, args.top_accounts, token, args)
    
    total_repos = len(set(star['id'] for star, _ in all_stars))
    print(f"\n{Fore.CYAN}Total stars considered: {Fore.GREEN}{total_stars_considered}")
    print(f"{Fore.CYAN}Total unique repositories: {Fore.GREEN}{total_repos}")
    
    display_distribution(all_stars)
    
    sorted_repos = create_ranking(all_stars, args.final_ranking, initial_ignored)
    
    # Generate timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Write repository data before displaying
    write_repo_data(sorted_repos, initial_ignored, timestamp)
    
    display_ranking(sorted_repos, interactive=not args.no_interactive, all_stars=all_stars, initial_ignored=initial_ignored)
    
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.YELLOW}Analysis Complete")
    print(f"{Fore.CYAN}Total stars considered: {Fore.GREEN}{total_stars_considered}")
    print(f"{Fore.CYAN}{'=' * 60}")
