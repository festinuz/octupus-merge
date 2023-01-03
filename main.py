import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import requests


def get_pr_url(issue: Dict[str, Any]) -> Optional[str]:
    if not 'pull_request' in issue:
        return None
    pr_info = issue['pull_request']
    if pr_info is None:
        return None
    pr_url = pr_info['url']
    return pr_url


def get_pr_urls(token: str, repository: str, label: str) -> List[str]:
    print(f'Getting issues for repository "{repository}"')
    response = requests.get(
        f'https://api.github.com/repos/{repository}/issues',
        params={'labels': label},
        headers={'Authorization': f'token {token}'},
    )
    resp_json = response.json()
    assert response.status_code == 200, resp_json
    pr_urls = []
    issues = response.json()
    print(f'Got {len(issues)} issue(s)')
    for issue in issues:
        pr_url = get_pr_url(issue)
        if pr_url is None:
            continue
        pr_urls.append(pr_url)
    print(f'Got {len(pr_urls)} issue(s) with PR urls')
    return pr_urls


def get_branch_name(token: str, pr_url: str) -> Optional[str]:
    response = requests.get(
        pr_url, headers={'Authorization': f'token {token}'},
    )
    resp_json = response.json()
    assert response.status_code == 200, resp_json
    if resp_json['state'] != 'open':
        return None
    branch_name = resp_json['head']['ref']
    return branch_name


def get_branch_names(token: str, pr_urls: List[str]) -> List[str]:
    branch_names = list()
    for pr_url in pr_urls:
        branch_name = get_branch_name(token, pr_url)
        if branch_name is None:
            continue
        branch_names.append(branch_name)
    print(f'Got {len(branch_names)} branch(es)')
    return branch_names


def set_action_output(output_name: str, value: str) -> None:
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        f.write(f'{output_name}={value}\n')


def main():
    repository = os.environ['GITHUB_REPOSITORY']  # mercantille/backend
    labels = os.environ['INPUT_LABELS']  # deploy/testing
    token = os.environ['INPUT_GITHUB_TOKEN']
    pr_urls = get_pr_urls(token, repository, labels)
    branch_names = get_branch_names(token, pr_urls)
    set_action_output('branches', ' '.join(branch_names))
    set_action_output(
        'origin_branches', ' '.join(f'origin/{branch}' for branch in branch_names)
    )


if __name__ == "__main__":
    main()
