# Contributing

1. fork → branch → PR
2. keep changes cross-platform (termux/linux/macos/windows)
3. no new dependencies without a strong reason
4. match the existing code style (compact, no fluff)
5. run `python mwc.py --help` and a local crawl before submitting

## testing locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python mwc.py https://example.com -p 5 -d 1 --no-dirs
