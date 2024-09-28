# GitHub Analytics Tools

This repository contains Python scripts for analyzing GitHub user data, including following relationships and starred repositories.

## Scripts

1. `github_following.py`: Fetches and analyzes following relationships for a given GitHub user.
2. `github_stars.py`: Analyzes starred repositories of top GitHub users.

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/github-analytics-tools.git
   cd github-analytics-tools
   ```

2. Install the required dependencies:
   ```
   pip install requests tqdm
   ```

3. Create a `config.json` file in the root directory with the following content:
   ```json
   {
       "count": 5,
       "github_token": "your_github_token_here"
   }
   ```
   Replace `your_github_token_here` with your actual GitHub Personal Access Token.

## Usage

### github_following.py

This script fetches the accounts followed by a specified GitHub user and writes the data to a CSV file.

```
python github_following.py <username> [--count <number>]
```

- `<username>`: The GitHub username to analyze
- `--count`: (Optional) Number of following accounts to fetch (default: 100)

Example:
```
python github_following.py octocat --count 50
```

### github_stars.py

This script analyzes the starred repositories of top GitHub users and creates a ranking.

```
python github_stars.py [--top-accounts <number>] [--top-repos <number>]
```

- `--top-accounts`: (Optional) Number of top accounts to consider (default: 100)
- `--top-repos`: (Optional) Number of top repositories to display (default: 40)

Example:
```
python github_stars.py --top-accounts 200 --top-repos 50
```

## Output

- `github_following.py` generates a `github_following.csv` file with following data.
- `github_stars.py` displays a ranking of repositories in the console.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool is for educational purposes only. Make sure to comply with GitHub's terms of service and API usage limits when using these scripts.
# GitHub Stars Analysis

This project analyzes the starred repositories of top GitHub users to identify trending and popular repositories.

## Features

- Fetches starred repositories of top GitHub users
- Ranks repositories based on their popularity among these users
- Filters out ignored repositories
- Displays a dynamic ranking as it processes each account
- Shows a final ranking of the most popular repositories

## Requirements

- Python 3.6+
- Required Python packages (install using `pip install -r requirements.txt`):
  - requests
  - tqdm
  - colorama
  - python-dotenv

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/github-stars-analysis.git
   cd github-stars-analysis
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your GitHub token:
   ```
   GITHUB_TOKEN=your_github_token_here
   ```

4. (Optional) Create an `ignored_repos.txt` file to list repositories you want to ignore:
   ```
   # List of repositories to ignore
   # Add one repository per line in the format "owner/repo"
   owner1/repo1
   owner2/repo2
   ```

## Usage

Run the script with:

```
python github_stars.py
```

Optional arguments:
- `--top-accounts`: Number of top accounts to consider (default: 100)
- `--top-repos`: Number of top repositories to display (default: 50)
- `--final-ranking`: Number of items to show in the final ranking (default: 50)

Example:
```
python github_stars.py --top-accounts 200 --top-repos 100 --final-ranking 75
```

## Configuration

- `config.json`: Contains the number of stars to fetch per user
- `.env`: Stores your GitHub token
- `ignored_repos.txt`: List of repositories to ignore in the analysis

## Output

The script will display:
1. A progress bar showing the processing of accounts
2. A dynamic ranking after processing each account
3. A final ranking of the most popular repositories

Each repository in the ranking will show:
- Its rank
- The repository name
- The number of accounts that starred it
- The usernames of those accounts
- The repository URL

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
