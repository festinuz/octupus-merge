foobar

__WIP, please dont use anywhere important__

Find all open PRs that have matching tags, octopus-merge them and push to remote.

For example, merge all branches with tag "test" and push the result to "testing" branch:
```yaml
name: Octopus-merge to testing
on:
  workflow_dispatch:
  push:
    branches:
      - "master"
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: '0'

      - name: Merge PRs found by tags
        id: octopus_merge
        uses: festinuz/octupus-merge@master
        with:
          github_token: ${{ github.token }}
          source_branch: master  # branch used as base for merge
          target_branch: testing  # branch that will be pushed to
          labels: test  # labels you want to match, comma-separated
```
