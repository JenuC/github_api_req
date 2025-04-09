
import requests
import os
import re

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

def get_repo_metadata(repo_full_name):
    url = f"https://api.github.com/repos/{repo_full_name}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return {
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "open_issues": data["open_issues_count"],
        "default_branch": data["default_branch"]
    }
    
def get_total_commits(repo_full_name, branch):
    url = f"https://api.github.com/repos/{repo_full_name}/commits?sha={branch}&per_page=1"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    link_header = response.headers.get("Link", "")
    if 'rel="last"' in link_header:
        match = re.search(r'&page=(\d+)>; rel="last"', link_header)
        if match:
            return int(match.group(1))
    return 1  # fallback if only one page


def get_total_pull_requests(repo_full_name):
    url = f"https://api.github.com/search/issues?q=repo:{repo_full_name}+type:pr"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["total_count"]

def get_top_contributors(repo_full_name, top_n=3):
    url = f"https://api.github.com/repos/{repo_full_name}/contributors?per_page={top_n}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return {
        contributor["login"]: contributor["contributions"]
        for contributor in response.json()
    }


def analyze_repo(repo_full_name):
    try:
        print(f"📁 {repo_full_name}")
        meta = get_repo_metadata(repo_full_name)
        branches = list_branches(repo_full_name)
        commit_info = get_commit_dates(repo_full_name, meta["default_branch"])
        total_commits = get_total_commits(repo_full_name, meta["default_branch"])
        pr_count = get_total_pull_requests(repo_full_name)
        contributors = get_top_contributors(repo_full_name)

        print(f"   🕐 First commit: {commit_info[0]}")
        print(f"   🕓 Last commit:  {commit_info[1]}")
        print(f"   🔢 Total commits: {total_commits}")
        print(f"   📬 PRs: {pr_count}")
        print(f"   🌟 Stars: {meta['stars']}, 🍴 Forks: {meta['forks']}, 🐞 Issues: {meta['open_issues']}")
        print(f"   👥 Top contributors: {contributors}")

        return {
            "branches": branches,
            "first_commit": commit_info[0],
            "last_commit": commit_info[1],
            "total_commits": total_commits,
            "pull_requests": pr_count,
            "stars": meta["stars"],
            "forks": meta["forks"],
            "open_issues": meta["open_issues"],
            "top_contributors": contributors
        }
    except Exception as e:
        print(f"⚠️ Error analyzing {repo_full_name}: {e}")
        return None

def list_org_repos(org, include_private=True):
    url = f"https://api.github.com/orgs/{org}/repos?per_page=100&type=all"
    repos = []
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        repos += response.json()
        url = response.links.get('next', {}).get('url')
    return [r for r in repos if include_private or not r["private"]]


def analyze_org_repos():
    org = os.getenv("GITHUB_ORG")
    if not org:
        print("⚠️ No organization name set in .env (GITHUB_ORG)")
        return

    print(f"🔍 Analyzing organization repos for: {org}")
    repos = list_org_repos(org)
    org_repo_data = {}

    for repo in repos:
        full_name = repo["full_name"]
        result = analyze_repo(full_name)
        if result:
            org_repo_data[full_name] = result

    return org_repo_data
