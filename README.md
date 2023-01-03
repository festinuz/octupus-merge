__WIP, please dont use anywhere important__

Find all open PRs that have matching tags and get their branch names for use in other steps.

For example, merge all branches with tag "test" and push the result to "testing" branch:
```yaml
name: Octopus-merge to testing
on: workflow_dispatch
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: '0'

      - name: Get branch names by labels
        id: branch_names
        uses: festinuz/octupus-merge@master
        with:
          github_token: ${{ github.token }}
          labels: test  # labels you want to match, comma-separated

      - name: Push changes to test branch
        # go to 'testing branch', use 'master' as base
        # merge all branches that mathed from labels
        # push branch to origin
        run: |
          git config --global user.email "noreply@github.com"
          git config --global user.name "octomerger"
          git checkout testing
          git reset --hard master --
          git merge --squash master ${{ steps.branch_names.outputs.origin_branches }} \
            && git commit -m "Merge branches found by labels" \
            || echo "Nothing to merge"
          git push origin HEAD --force
```
