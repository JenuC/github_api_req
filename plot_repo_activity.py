import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Load the JSON file
with open("github_repos.json") as f:
    data = json.load(f)

repos = []
start_dates = []
durations = []

# Extract and format the data
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
repos, start_dates, durations = zip(*sorted(zip(repos, start_dates, durations), key=lambda x: x[1]))

# Plot
fig, ax = plt.subplots(figsize=(10, len(repos) * 0.4))
ax.barh(repos, durations, left=start_dates, height=0.4)

# Format x-axis as dates
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.xlabel("Date")
plt.title("GitHub Repo Activity Durations (First → Last Commit)")
plt.tight_layout()
plt.grid(True, axis='x', linestyle='--', alpha=0.4)
plt.show()
