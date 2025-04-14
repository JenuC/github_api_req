import requests
import json
from dotenv import load_dotenv
from gather_github_data import list_repos,list_branches,get_commit_dates 
from gather_github_data import get_repo_metadata, get_top_contributors, get_total_commits, get_total_pull_requests
from gather_github_data import GITHUB_USER
from gather_github_data import analyze_repo, analyze_org_repos, load_existing_repo_data
load_dotenv()



def main():
    print(f"Fetching repositories for: {GITHUB_USER}")
    repos = list_repos(GITHUB_USER)
    repo_data = {}
    existing_data = load_existing_repo_data('github_repos.json')
    for repo in repos:
        name = repo["name"]
        full_name = repo["full_name"]
        if not full_name.startswith('JenuC'):
            full_name = r'JenuC/'+full_name
        if full_name in existing_data:
            print(f"✅ Skipping already processed repo: {full_name}")
            continue
        result = analyze_repo(full_name)
        
    custom_repos = ["spicyfoodie/ij_macros"]
    for repo_full_name in custom_repos:
        if repo_full_name in existing_data:
            print(f"✅ Skipping already processed repo: {repo_full_name}")
            continue
        result = analyze_repo(repo_full_name)
        if result:
            repo_data[repo_full_name] = result

    # Save output
    with open("github_repos.json", "w") as f:
        json.dump(repo_data, f, indent=2)
    print("✅ Repo data saved to github_repos.json")

    org_repo_data = analyze_org_repos()
    with open("github_org_repos.json", "w") as f:
        json.dump(org_repo_data, f, indent=2)
    print("✅ Saved organization repo data to github_org_repos.json")


if __name__ == "__main__":
    main()
