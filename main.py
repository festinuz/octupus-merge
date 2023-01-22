import argparse
import dataclasses
import os
import subprocess
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import requests


COMMIT_MESSAGE_TPL = """\
Merge branches found by label

Merged branches:
{}
"""


@dataclasses.dataclass
class PullRequest:
    url: str
    branch_name: str


def get_pr_url(issue: Dict[str, Any]) -> Optional[str]:
    if not 'pull_request' in issue:
        return None
    pr_info = issue['pull_request']
    if pr_info is None:
        return None
    pr_url = pr_info['url']
    return pr_url


def get_pr_urls(token: str, repository: str, labels: str) -> List[str]:
    print(f'Getting issues for repository "{repository}"')
    response = requests.get(
        f'https://api.github.com/repos/{repository}/issues',
        params={'labels': ','.join(labels)},
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


def get_pull_request(token: str, url: str) -> Optional[PullRequest]:
    response = requests.get(
        url, headers={'Authorization': f'token {token}'},
    )
    resp_json = response.json()
    assert response.status_code == 200, resp_json
    if resp_json['state'] != 'open':
        print('Pull request is not open, skipping')
        return None
    branch_name = resp_json['head']['ref']
    pull_request = PullRequest(
        url=url,
        branch_name=branch_name,
    )
    return pull_request


def get_pull_requests(
        token: str,
        repository: str,
        labels: List[str],
) -> List[PullRequest]:
    pr_urls = get_pr_urls(token, repository, labels)
    pull_requests = list()
    for url in pr_urls:
        pull_request = get_pull_request(token, url)
        if pull_request is None:
            continue
        pull_requests.append(pull_request)
    print(f'Got {len(pull_requests)} pull request(s)')
    return pull_requests


def execute_shell_command(command: str) -> None:
    print(f'Executing shell command: {command}')
    result = subprocess.run(command, shell=True)
    result.check_returncode()


def push_to_remote() -> None:
    execute_shell_command('git push origin HEAD --force')


def prepare_target_branch(
        source_branch: str,
        target_branch: str,
) -> None:
    execute_shell_command('git config --global user.email "noreply@github.com"')
    execute_shell_command('git config --global user.name "octomerger"')
    execute_shell_command('git fetch origin')
    execute_shell_command(f'git checkout {target_branch}')
    execute_shell_command(f'git reset --hard {source_branch} --')


def merge_pr_branches(pull_requests: List[PullRequest]) -> None:
    if len(pull_requests) == 0:
        print('No pull requests to merge')
        return
    origin_branches = ' '.join(
        f'origin/{pr.branch_name}' for pr in pull_requests
    )
    execute_shell_command(f'git merge --squash {origin_branches}')
    pr_messages = ['* {pr.branch_name}:{pr.url}' for pr in pull_requests]
    merged_prs = '\n'.join(pr_messages)
    commit_msg = COMMIT_MESSAGE_TPL.format(merged_prs)
    execute_shell_command(f"git commit -m '{commit_msg}'")


def push_to_target_branch() -> None:
    execute_shell_command('git push origin HEAD --force')


def perform_octomerge(
        token: str,
        repository: str,
        source_branch: str,
        target_branch: str,
        labels: List[str],
) -> None:
    pull_requests = get_pull_requests(token, repository, labels)
    prepare_target_branch(source_branch, target_branch)
    merge_pr_branches(pull_requests)
    push_to_target_branch()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', type=str, required=True)
    parser.add_argument('--source-branch', type=str, required=True)
    parser.add_argument('--target-branch', type=str, required=True)
    parser.add_argument('--labels', type=str, required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    print(args)
    perform_octomerge(
        token=args.token,
        repository=os.environ['GITHUB_REPOSITORY'],
        source_branch=args.source_branch,
        target_branch=args.target_branch,
        labels=args.labels.split(','),
    )


if __name__ == "__main__":
    main()
