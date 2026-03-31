# GitHub CLI Cheatsheet

## Install / Login

```bash
sudo apt-get update
sudo apt-get install -y gh
gh --version
gh auth login
gh auth status
```

## Repo

```bash
gh repo view
gh repo clone owner/repo
gh repo view --web
```

## Issues

```bash
gh issue list
gh issue view 123
gh issue create
```

## Pull Requests

```bash
gh pr list
gh pr status
gh pr view 123
gh pr checkout 123
gh pr create
gh pr view --web
```

## Actions / CI

```bash
gh run list
gh run view <run-id>
gh run watch
```

## Useful Daily Commands

```bash
gh pr status
gh issue list
gh run list
```

## Notes

- Install requires your system password because `apt` uses `sudo`
- After install, run `gh auth login`
- If browser login is inconvenient, `gh auth login` also supports token-based login
