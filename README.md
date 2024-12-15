<div align="center">

# 🌟 GitHub Analytics Tools

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![GitHub API](https://img.shields.io/badge/GitHub-API-green.svg?style=flat-square&logo=github)](https://docs.github.com/en/rest)

Powerful Python scripts for analyzing GitHub user data, including following relationships and starred repositories.

</div>

## 🚀 Features

- 📊 Analyze following relationships between GitHub users
- ⭐ Track and rank starred repositories
- 📈 Generate detailed statistics and reports
- 🔄 Real-time data processing
- 📋 CSV export functionality

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/github-analytics-tools.git
cd github-analytics-tools
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your GitHub token:
   - Create a `config.json` file:
```json
{
    "count": 5,
    "github_token": "your_github_token_here"
}
```
   - Or use environment variables:
```bash
export GITHUB_TOKEN=your_github_token_here
```

## 📚 Usage

### Following Analysis

```bash
python github_following.py <username> [--count <number>]
```

Options:
- `username`: Target GitHub username
- `--count`: Number of following accounts to analyze (default: 100)

### Stars Analysis

```bash
python github_stars.py [--top-accounts <number>] [--top-repos <number>]
```

Options:
- `--top-accounts`: Number of top accounts to analyze (default: 100)
- `--top-repos`: Number of top repositories to show (default: 40)
- `--final-ranking`: Items in final ranking (default: 50)

## 📋 Configuration Files

- `config.json`: Basic settings
- `.env`: Environment variables
- `ignored_repos.txt`: Repositories to exclude

## 📊 Output

- CSV files with following data
- Console-based repository rankings
- Detailed statistics and reports

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Fork the repository
- Create a feature branch
- Submit a Pull Request

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes. Please comply with GitHub's terms of service and API usage limits.
