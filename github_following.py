#!/usr/bin/env python3

import requests
import json

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

def display_following(username, following):
    print(f"Accounts followed by {username}:")
    for i, account in enumerate(following, 1):
        print(f"{i}. {account['login']} - {account['html_url']}")

if __name__ == "__main__":
    config_file = 'config.json'
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    count = config['count']
    for username in config['accounts']:
        following = get_following(username, count)
        display_following(username, following)
        print()  # Add a blank line between accounts
