import os
import requests
import json
from dotenv import load_dotenv
import re

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

def get_commit_dates(repo_full_name, branch):
    base_url = f"https://api.github.com/repos/{repo_full_name}/commits"

    # Get latest commit
    latest_commit = requests.get(
        f"{base_url}?sha={branch}&per_page=1",
        headers=headers
    ).json()[0]
    last_date = latest_commit["commit"]["committer"]["date"]

    # Get first commit (via last page of commits)
    first_page = requests.get(f"{base_url}?sha={branch}&per_page=1", headers=headers)
    link_header = first_page.headers.get("Link", "")
    last_page = 1
    if 'rel="last"' in link_header:
        match = re.search(r'&page=(\d+)>; rel="last"', link_header)
        if match:
            last_page = int(match.group(1))

    oldest_commit = requests.get(
        f"{base_url}?sha={branch}&per_page=1&page={last_page}",
        headers=headers
    ).json()[0]
    first_date = oldest_commit["commit"]["committer"]["date"]

    return first_date, last_date


def main():
    print(f"Fetching repositories for: {GITHUB_USER}")
    repos = list_repos(GITHUB_USER)
    repo_data = {}

    for repo in repos:
        name = repo["name"]
        full_name = repo["full_name"]
        default_branch = repo["default_branch"]
        print(f"📁 {name}")
        try:
            branches = list_branches(full_name)
            commit_info = get_commit_dates(full_name, default_branch)
            for branch in branches:
                print(f"   └── {branch}")
            print(f"   🕐 First commit: {commit_info[0]}")
            print(f"   🕓 Last commit:  {commit_info[1]}")
            repo_data[name] = {
            "branches": branches,
            "first_commit": commit_info[0],
            "last_commit": commit_info[1]
            }
        except requests.HTTPError as e:
            print(f"   ❌ Failed to fetch branches: {e}")

    # Save output
    with open("github_repos.json", "w") as f:
        json.dump(repo_data, f, indent=2)
    print("✅ Repo data saved to github_repos.json")

if __name__ == "__main__":
    main()
