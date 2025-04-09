import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def load_repo_data(filepath):
    with open(filepath) as f:
        data = json.load(f)

    repos = []
    start_dates = []
    durations = []

    for repo, info in data.items():
        try:
            start = datetime.fromisoformat(info["first_commit"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(info["last_commit"].replace("Z", "+00:00"))
            repos.append(repo)
            start_dates.append(start)
            durations.append((end - start).days)
        except Exception as e:
            print(f"⚠️ Skipping {repo}: {e}")
    
    # Sort by start date
    return zip(*sorted(zip(repos, start_dates, durations), key=lambda x: x[1]))

# Load both personal and org data
personal = load_repo_data("github_repos.json")
org = load_repo_data("github_org_repos.json")

# Create subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

def plot_gantt(ax, repos, starts, durations, title):
    ax.barh(repos, durations, left=starts, height=0.4)
    ax.set_title(title)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.grid(True, axis='x', linestyle='--', alpha=0.4)
    ax.set_ylabel("Repositories")

plot_gantt(ax1, *personal, "🧍 Personal & Custom Repos")
plot_gantt(ax2, *org, "🏢 Organization Repos")

plt.xlabel("Timeline (First → Last Commit)")
plt.tight_layout()
plt.show()
