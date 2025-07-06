import requests
import pandas as pd
import os
import json

# ==============================================================================
# --- Configuration ---
# ==============================================================================
# Set the search mode. Options are: 'TOPICS', 'ORG', 'USER'
SEARCH_MODE = 'TOPICS'

# --- Search Terms ---
# For 'TOPICS' mode, provide a list of topics.
# The script will find repos that have ALL of these topics.
SEARCH_TOPICS = ["r01ca230551"]

# For 'ORG' mode, provide the organization's name.
SEARCH_ORG = "waldronlab"

# For 'USER' mode, provide the user's GitHub handle.
SEARCH_USER = "lwaldron"
# ==============================================================================

# --- Build the search query based on the selected mode ---
query_parts = []
if SEARCH_MODE == 'TOPICS':
    query_parts = [f"topic:{topic}" for topic in SEARCH_TOPICS]
    print(f"Searching for repositories with topics: {SEARCH_TOPICS}")
elif SEARCH_MODE == 'ORG':
    query_parts.append(f"org:{SEARCH_ORG}")
    print(f"Searching for repositories in organization: {SEARCH_ORG}")
elif SEARCH_MODE == 'USER':
    query_parts.append(f"user:{SEARCH_USER}")
    print(f"Searching for repositories for user: {SEARCH_USER}")

search_query = "+".join(query_parts)
url = f"https://api.github.com/search/repositories?q={search_query}&per_page=100"

# --- The rest of the script remains the same ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else None

if not GITHUB_TOKEN:
    print("Warning: GITHUB_TOKEN environment variable not set.")

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    projects = []
    repo_list_for_json = []

    for item in data["items"]:
        projects.append({
            "Repository Name": item["name"],
            "Owner": item["owner"]["login"],
            "Description": item["description"],
            "Stars": item["stargazers_count"],
            "Last Updated": item["updated_at"],
            "URL": item["html_url"]
        })
        repo_list_for_json.append(item["full_name"])

    if projects:
        df = pd.DataFrame(projects)
        with open("projects.md", "w", encoding="utf-8") as f:
            f.write(f"# Projects Discovery\n\n")
            f.write(f"A list of repositories discovered on GitHub based on the configured search.\n\n")
            f.write(df.to_markdown(index=False))
        print(f"Successfully created projects.md with {len(projects)} projects.")

        with open("repositories.json", "w") as f:
            json.dump(repo_list_for_json, f)
        print(f"Successfully created repositories.json.")
    else:
        print(f"No projects found for the specified criteria.")

except requests.exceptions.HTTPError as e:
    print(f"Failed to retrieve data: {e.response.status_code}")
    print(f"Response: {e.response.text}")
    
