# Feishu CLI Cheatsheet

## Current Setup

- CLI command: `lark-cli`
- Config path: `/home/chengang/.lark-cli/config.json`
- Logged-in user Open ID: `ou_e980ab0433f84644545ae83c1ce08ca4`

## Basic Checks

```bash
source ~/.bashrc
lark-cli auth status --verify
lark-cli doctor
```

## Help

```bash
lark-cli --help
lark-cli im --help
lark-cli contact --help
lark-cli docs --help
lark-cli sheets --help
```

## Auth

```bash
lark-cli auth list
lark-cli auth status
lark-cli auth logout
```

## Useful Next Steps

- Search users:

```bash
lark-cli contact +search-user --query "name"
```

- View IM commands:

```bash
lark-cli im --help
```

- View schema for a specific method:

```bash
lark-cli schema im.message.create --format pretty
```

## Notes

- Open a new terminal or run `source ~/.bashrc` before using `lark-cli`.
- The command name is `lark-cli`, not `lark`.
- If a command fails, run `lark-cli doctor` first.
