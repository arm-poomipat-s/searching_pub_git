import requests
import time

headers = {
    'Authorization': 'github_authorization_token'
}

def handle_rate_limiting(response):
    if response.status_code == 403:
        if 'X-RateLimit-Remaining' in response.headers and response.headers['X-RateLimit-Remaining'] == '0':
            reset_time = int(response.headers['X-RateLimit-Reset'])
            sleep_time = reset_time - int(time.time())
            print(f"Rate limit exceeded. Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
            return True
    return False

def get_pull_request_count(repo):
    pr_url = f"https://api.github.com/repos/{repo['full_name']}/pulls?state=all&per_page=100"
    pr_count = 0
    page = 1
    while True:
        pr_response = requests.get(f"{pr_url}&page={page}", headers=headers)
        if handle_rate_limiting(pr_response):
            continue
        if pr_response.status_code == 200:
            pr_page_data = pr_response.json()
            pr_count += len(pr_page_data)
            if len(pr_page_data) < 100:
                break
            page += 1
        else:
            print(f"Failed to retrieve pull requests for {repo['full_name']}: {pr_response.status_code}")
            break
    return pr_count

query = 'language:Python'
url = f'https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=20'

response = requests.get(url, headers=headers)
if handle_rate_limiting(response):
    response = requests.get(url, headers=headers)

if response.status_code == 200:
    repositories = response.json()['items']
    for repo in repositories:
        pr_count = get_pull_request_count(repo)
        if pr_count is not None:
            print(f"Name: {repo['name']}, Stars: {repo['stargazers_count']}, Pull Requests: {pr_count}")
else:
    print(f"Failed to retrieve repositories: {response.status_code}")
