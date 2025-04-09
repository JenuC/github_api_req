import os
import requests
import json
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()
GITHUB_USER = os.getenv("GITHUB_USER")
TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def list_repos(user, include_private=True):
    url = f"https://api.github.com/user/repos?per_page=100&affiliation=owner"
    repos = []
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        repos += response.json()
        url = response.links.get('next', {}).get('url')
    return [r for r in repos if include_private or not r["private"]]

def list_branches(repo_full_name):
    url = f"https://api.github.com/repos/{repo_full_name}/branches"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return [branch["name"] for branch in response.json()]

def main():
    print(f"Fetching repositories for: {GITHUB_USER}")
    repos = list_repos(GITHUB_USER)
    repo_data = {}

    for repo in repos:
        name = repo["name"]
        full_name = repo["full_name"]
        print(f"📁 {name}")
        try:
            branches = list_branches(full_name)
            for branch in branches:
                print(f"   └── {branch}")
            repo_data[name] = branches
        except requests.HTTPError as e:
            print(f"   ❌ Failed to fetch branches: {e}")

    # Save output
    with open("github_repos.json", "w") as f:
        json.dump(repo_data, f, indent=2)
    print("✅ Repo data saved to github_repos.json")

if __name__ == "__main__":
    main()
