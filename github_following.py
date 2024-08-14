#!/usr/bin/env python3

import requests
import json
import csv
import os
import argparse
import time

def make_github_request(url, params=None):
    max_retries = 5
    base_delay = 1

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403 and 'rate limit exceeded' in str(e).lower():
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"Error: Rate limit exceeded. Max retries reached.")
                    return None
            else:
                print(f"HTTP error occurred: {e}")
                return None
        except requests.RequestException as e:
            print(f"Error: Unable to fetch data. {e}")
            return None
        
        time.sleep(1)  # Add a small delay between requests

def get_following(username, count=100):
    url = f"https://api.github.com/users/{username}/following"
    params = {"per_page": count}
    
    following = make_github_request(url, params)
    
    if following is None:
        return []
    elif not following:
        print(f"No following accounts found for {username}")
        return []
    
    return following

def get_follower_count(username):
    url = f"https://api.github.com/users/{username}"
    
    user_data = make_github_request(url)
    
    if user_data is None:
        return None
    
    return user_data.get('followers')

def write_to_csv(username, following, csv_file):
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Account', 'Followers', 'Following'])
        
        existing_accounts = set()
        if file_exists:
            with open(csv_file, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                existing_accounts = set(row[0] for row in reader)
        
        for account in following:
            if account['login'] not in existing_accounts:
                follower_count = get_follower_count(account['login'])
                if follower_count is not None:
                    writer.writerow([account['login'], follower_count, username])
                else:
                    print(f"Skipping {account['login']} due to error fetching follower count")

def display_following(username, following):
    print(f"Accounts followed by {username}:")
    for i, account in enumerate(following, 1):
        follower_count = get_follower_count(account['login'])
        print(f"{i}. {account['login']} - {account['html_url']} (Followers: {follower_count})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch GitHub following accounts")
    parser.add_argument("username", help="GitHub username to fetch following accounts for")
    parser.add_argument("--count", type=int, default=100, help="Number of following accounts to fetch (default: 100)")
    args = parser.parse_args()

    username = args.username
    count = args.count
    
    following = get_following(username, count)
    display_following(username, following)
    
    csv_file = 'github_following.csv'
    write_to_csv(username, following, csv_file)
    print(f"\nData has been written to {csv_file}")
