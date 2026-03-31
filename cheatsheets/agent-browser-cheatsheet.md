# Agent Browser Cheatsheet

## Basic Setup

```bash
source ~/.bashrc
agent-browser --help
```

## Open / Inspect / Close

```bash
agent-browser open https://example.com
agent-browser snapshot -i
agent-browser get title
agent-browser get url
agent-browser close
```

## Click / Fill / Type

```bash
agent-browser click @e2
agent-browser fill "#email" "test@example.com"
agent-browser fill "#password" "secret"
agent-browser click "#submit"
```

## Screenshot / PDF

```bash
agent-browser screenshot /home/chengang/page.png
agent-browser screenshot --full /home/chengang/full.png
agent-browser screenshot --annotate /home/chengang/annotated.png
agent-browser pdf /home/chengang/page.pdf
```

## Wait / Scroll

```bash
agent-browser wait 2000
agent-browser wait "#submit"
agent-browser scroll down 800
agent-browser scrollintoview "#footer"
```

## Useful Queries

```bash
agent-browser get text @e1
agent-browser get html body
agent-browser get attr "#login" href
agent-browser find role button click --name "Submit"
```

## Session Tips

```bash
agent-browser --session work open https://example.com
agent-browser --session work snapshot -i
agent-browser --session work close
```

## Real Example

```bash
agent-browser open https://example.com
agent-browser wait 2000
agent-browser snapshot -i
agent-browser screenshot /home/chengang/agent-browser-example.png
agent-browser close
```

## Notes

- CLI path: `/home/chengang/.npm-global/bin/agent-browser`
- Existing Chrome detected on this machine
- Best practice: run `snapshot -i` first, then click elements by `@ref`
