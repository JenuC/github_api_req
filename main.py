import requests
import json
from dotenv import load_dotenv
from gather_github_data import list_repos,list_branches,get_commit_dates 
from gather_github_data import get_repo_metadata, get_top_contributors, get_total_commits, get_total_pull_requests
from gather_github_data import GITHUB_USER
from gather_github_data import analyze_repo
# Load credentials from .env
load_dotenv()



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
            meta = get_repo_metadata(full_name)
            commit_info = get_commit_dates(full_name, meta["default_branch"])
            total_commits = get_total_commits(full_name, meta["default_branch"])
            pr_count = get_total_pull_requests(full_name)
            contributors = get_top_contributors(full_name)

            print(f"   └── branches: {branches}")
            print(f"   🕐 First commit: {commit_info[0]}")
            print(f"   🕓 Last commit:  {commit_info[1]}")
            print(f"   🔢 Total commits: {total_commits}")
            print(f"   📬 PRs: {pr_count}")
            print(f"   🌟 Stars: {meta['stars']}, 🍴 Forks: {meta['forks']}, 🐞 Issues: {meta['open_issues']}")
            print(f"   👥 Top contributors: {contributors}")

            repo_data[name] = {
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

        except requests.HTTPError as e:
            print(f"   ❌ Failed to fetch: {e}")

        # Save output
        with open("github_repos.json", "w") as f:
            json.dump(repo_data, f, indent=2)
        print("✅ Repo data saved to github_repos.json")
        
        
        
        break
    
    custom_repos = ["spicyfoodie/ij_macros"]

    for repo_full_name in custom_repos:
        result = analyze_repo(repo_full_name)
        if result:
            repo_data[repo_full_name] = result
            with open("github_repos.json", "w") as f:
                json.dump(repo_data, f, indent=2)
            print("✅ Repo data saved to github_repos.json")




if __name__ == "__main__":
    main()
