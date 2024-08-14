#!/usr/bin/env python3

import requests
import json
import csv
import sys
import os

def get_following(username, count=100):
    url = f"https://api.github.com/users/{username}/following"
    params = {
        "per_page": count
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error: Unable to fetch data for {username}. {e}")
        return []
    
    following = response.json()
    
    if not following:
        print(f"No following accounts found for {username}")
        return []
    
    return following

def get_follower_count(username):
    url = f"https://api.github.com/users/{username}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        user_data = response.json()
        return user_data['followers']
    except requests.RequestException as e:
        print(f"Error: Unable to fetch follower count for {username}. {e}")
        return None

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
                writer.writerow([account['login'], follower_count, username])

def display_following(username, following):
    print(f"Accounts followed by {username}:")
    for i, account in enumerate(following, 1):
        print(f"{i}. {account['login']} - {account['html_url']}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./github_following.py <username>")
        sys.exit(1)

    username = sys.argv[1]
    config_file = 'config.json'
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    count = config['count']
    following = get_following(username, count)
    display_following(username, following)
    
    csv_file = 'github_following.csv'
    write_to_csv(username, following, csv_file)
    print(f"\nData has been written to {csv_file}")
