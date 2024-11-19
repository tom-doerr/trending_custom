#!/usr/bin/env python3

import os
import requests
from datetime import datetime
import time
from dotenv import load_dotenv

def get_rate_limits():
    """Get GitHub API rate limit information"""
    load_dotenv()
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("Error: GITHUB_TOKEN not found in .env file")
        return None

    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    try:
        # Get rate limit info
        response = requests.get('https://api.github.com/rate_limit', headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error accessing GitHub API: {e}")
        return None

def format_time_until_reset(reset_timestamp):
    """Format the time until rate limit reset"""
    now = datetime.now().timestamp()
    time_left = reset_timestamp - now
    
    if time_left <= 0:
        return "Reset time has passed"
    
    minutes, seconds = divmod(int(time_left), 60)
    hours, minutes = divmod(minutes, 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    
    return " ".join(parts)

def display_api_status():
    """Display GitHub API status information"""
    rate_limits = get_rate_limits()
    if not rate_limits:
        return

    print("\nGitHub API Status:")
    print("=" * 50)

    # Integration manifest API limits
    integration = rate_limits['resources']['integration_manifest']
    print("\nIntegration Manifest API:")
    print(f"  Remaining calls: {integration['remaining']}/{integration['limit']}")
    print(f"  Reset in: {format_time_until_reset(integration['reset'])}")
    print(f"  Usage: {((integration['limit'] - integration['remaining']) / integration['limit'] * 100):.1f}%")

    # Graphql API limits
    graphql = rate_limits['resources']['graphql']
    print("\nGraphQL API:")
    print(f"  Remaining calls: {graphql['remaining']}/{graphql['limit']}")
    print(f"  Reset in: {format_time_until_reset(graphql['reset'])}")
    print(f"  Usage: {((graphql['limit'] - graphql['remaining']) / graphql['limit'] * 100):.1f}%")

    # Search API limits
    search = rate_limits['resources']['search']
    print("\nSearch API:")
    print(f"  Remaining calls: {search['remaining']}/{search['limit']}")
    print(f"  Reset in: {format_time_until_reset(search['reset'])}")
    print(f"  Usage: {((search['limit'] - search['remaining']) / search['limit'] * 100):.1f}%")

    # Core API limits
    core = rate_limits['resources']['core']
    print("\nCore API:")
    print(f"  Remaining calls: {core['remaining']}/{core['limit']}")
    print(f"  Reset in: {format_time_until_reset(core['reset'])}")
    print(f"  Usage: {((core['limit'] - core['remaining']) / core['limit'] * 100):.1f}%")

if __name__ == "__main__":
    display_api_status()
