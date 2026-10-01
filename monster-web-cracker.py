#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════════════════╗
# ║                                                                      ║
# ║              ███╗   ███╗██████╗     ██╗  ██╗ █████╗ ██╗  ██╗        ║
# ║              ████╗ ████║██╔══██╗    ██║  ██║██╔══██╗╚██╗██╔╝        ║
# ║              ██╔████╔██║██████╔╝    ███████║███████║ ╚███╔╝         ║
# ║              ██║╚██╔╝██║██╔══██╗    ██╔══██║██╔══██║ ██╔██╗         ║
# ║              ██║ ╚═╝ ██║██║  ██║    ██║  ██║██║  ██║██╔╝ ██╗        ║
# ║              ╚═╝     ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝        ║
# ║                                                                      ║
# ║                     O R   /   O R A C L E   /   R I S E              ║
# ║                                                                      ║
# ╠══════════════════════════════════════════════════════════════════════╣
# ║                                                                      ║
# ║     MONSTER WEB CRACKER  ·  v5.0  ·  MODERN EDITION                  ║
# ║     deep crawler · async engine · secret hunter · endpoint miner     ║
# ║                                                                      ║
# ║     AUTHOR  ::  MR HAXOR                                             ║
# ║                                                                      ║
# ╚══════════════════════════════════════════════════════════════════════╝

import sys
import os
import re
import json
import time
import socket
import random
import hashlib
import platform
import threading
import argparse
from collections import deque
from datetime import datetime
from urllib.parse import (
    urlparse, urljoin, urldefrag, urlencode, parse_qs, urlunparse
)
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser

# ── platform detection ────────────────────────────────────────────
IS_WINDOWS = platform.system().lower().startswith("win")
IS_TERMUX  = ("com.termux" in os.environ.get("PREFIX", "") or
              os.path.exists("/data/data/com.termux"))
IS_LINUX   = platform.system().lower() == "linux" and not IS_TERMUX
IS_MAC     = platform.system().lower() == "darwin"

def _enable_ansi_windows():
    if not IS_WINDOWS:
        return
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetConsoleMode(k.GetStdHandle(-11), 7)
    except Exception:
        pass
    try:
        import colorama
        colorama.just_fix_windows_console()
    except Exception:
        pass

_enable_ansi_windows()

try:
    import requests
    from requests.adapters import HTTPAdapter
    try:
        from urllib3.util.retry import Retry
    except ImportError:
        from requests.packages.urllib3.util.retry import Retry
    try:
        requests.packages.urllib3.disable_warnings()
    except Exception:
        pass
except ImportError:
    print("[!] missing dependency: requests")
    print("    install:  pip install requests")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════════
#  MODERN PALETTE — NEON CYAN · MAGENTA · PURPLE · MINT
# ══════════════════════════════════════════════════════════════════════
C1  = "\033[38;5;51m"    # bright cyan
C2  = "\033[38;5;45m"    # cyan
C3  = "\033[38;5;39m"    # lighter cyan
C4  = "\033[38;5;33m"    # deep cyan
M1  = "\033[38;5;213m"   # hot magenta
M2  = "\033[38;5;207m"   # magenta
M3  = "\033[38;5;171m"   # purple-pink
P1  = "\033[38;5;141m"   # purple
P2  = "\033[38;5;99m"    # deep purple
MN1 = "\033[38;5;121m"   # mint
MN2 = "\033[38;5;84m"    # green-mint
W   = "\033[1;37m"
DW  = "\033[38;5;250m"
SL  = "\033[38;5;245m"   # slate
DIM = "\033[2m"
BOLD= "\033[1m"
RED = "\033[38;5;203m"
YEL = "\033[38;5;221m"
GRN = "\033[38;5;120m"
RS  = "\033[0m"

LOCK = threading.Lock()

# ══════════════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════════════
VERSION   = "5.0"
TOOL_NAME = "MONSTER WEB CRACKER"
AUTHOR    = "MR HAXOR"
TAGLINE   = "Or / Oracle / Rise"

DEFAULT_TIMEOUT   = 20
MAX_PAGE_WORKERS  = 10
MAX_ASSET_WORKERS = 16
MAX_DIR_WORKERS   = 20

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) "
    "Gecko/20100101 Firefox/125.0",
]

# ══════════════════════════════════════════════════════════════════════
#  FILE-TYPE MAPS
# ══════════════════════════════════════════════════════════════════════
IMAGE_EXTS   = {".png",".jpg",".jpeg",".gif",".webp",".avif",".ico",
                ".bmp",".tiff",".tif"}
SVG_EXTS     = {".svg",".svgz"}
FONT_EXTS    = {".woff",".woff2",".ttf",".otf",".eot"}
DOC_EXTS     = {".pdf",".doc",".docx",".xls",".xlsx",".ppt",".pptx",
                ".csv",".txt",".rtf",".odt"}
MEDIA_EXTS   = {".mp4",".webm",".mp3",".ogg",".wav",".m4a",".flac"}
CODE_EXTS    = {".css",".js",".mjs",".ts",".jsx",".tsx",".map",
                ".json",".xml",".yaml",".yml"}
ARCHIVE_EXTS = {".zip",".tar",".gz",".rar",".7z",".bz2",".xz"}
SKIP_EXTS    = {".exe",".dmg",".apk",".iso",".img"}
HTML_EXTS    = {"",".html",".htm",".php",".asp",".aspx",".jsp",
                ".cfm",".cgi",".shtml",".xhtml"}

# ══════════════════════════════════════════════════════════════════════
#  DIRECTORY WORDLIST
# ══════════════════════════════════════════════════════════════════════
DIR_WORDLIST = [
    "admin","administrator","login","signin","dashboard","panel",
    "api","api/v1","api/v2","graphql","rest","rpc",
    "backup","backups","bak","old","archive",
    "config","configuration","settings","setup","install",
    "test","tests","testing","dev","development","staging","stage",
    "private","internal","secure","secret","hidden",
    "uploads","upload","files","file","media","assets","static",
    "images","img","css","js","scripts",
    "db","database","sql","mysql","dump","exports",
    "logs","log","debug","trace","errors",
    "docs","documentation","readme","manual",
    "user","users","account","accounts","profile","profiles",
    "register","signup","auth","oauth","sso",
    "wp-admin","wp-login","wp-content","wp-includes",
    "phpmyadmin","pma","adminer",
    ".git","/.git/config","/.env","/.env.local","/.env.production",
    "robots.txt","sitemap.xml","sitemap_index.xml",
    "crossdomain.xml","security.txt","humans.txt",
    "web.config",".htaccess","composer.json","package.json",
    "CHANGELOG","LICENSE","README","README.md",
    "server-status","server-info",
    "swagger","swagger-ui","openapi","api-docs",
    "actuator","actuator/health","health","healthz","status","ping",
    "metrics","prometheus","grafana",
    "phpinfo.php","info.php","test.php",
    "console","shell","cmd","terminal",
    "xmlrpc.php","cron","scheduler",
]

# ══════════════════════════════════════════════════════════════════════
#  SECRET ARSENAL
# ══════════════════════════════════════════════════════════════════════
SECRET_PATTERNS = [
    ("AWS Access Key",     re.compile(r"AKIA[0-9A-Z]{16}")),
    ("AWS Secret Key",     re.compile(r"(?i)aws.{0,20}['\"][0-9a-zA-Z/+]{40}['\"]")),
    ("Google API Key",     re.compile(r"AIza[0-9A-Za-z\-_]{35}")),
    ("GCP Service Acct",   re.compile(r'"type":\s*"service_account"')),
    ("GitHub Token",       re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,}")),
    ("GitLab Token",       re.compile(r"glpat-[A-Za-z0-9\-_]{20,}")),
    ("Slack Token",        re.compile(r"xox[baprs]-[A-Za-z0-9\-]{10,}")),
    ("Slack Webhook",      re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9/]{40,}")),
    ("Stripe Live",        re.compile(r"sk_live_[0-9a-zA-Z]{24,}")),
    ("Stripe Test",        re.compile(r"sk_test_[0-9a-zA-Z]{24,}")),
    ("Discord Token",      re.compile(r"[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27,}")),
    ("Discord Webhook",    re.compile(r"https://discord(?:app)?\.com/api/webhooks/\d+/[\w-]+")),
    ("Twilio SID",         re.compile(r"AC[a-f0-9]{32}")),
    ("SendGrid Key",       re.compile(r"SG\.[\w\-]{22}\.[\w\-]{43}")),
    ("Mailgun Key",        re.compile(r"key-[0-9a-zA-Z]{32}")),
    ("Private RSA Key",    re.compile(r"-----BEGIN RSA PRIVATE KEY-----")),
    ("Private EC Key",     re.compile(r"-----BEGIN EC PRIVATE KEY-----")),
    ("Private OpenSSH",    re.compile(r"-----BEGIN OPENSSH PRIVATE KEY-----")),
    ("Private PGP",        re.compile(r"-----BEGIN PGP PRIVATE KEY BLOCK-----")),
    ("JWT",                re.compile(r"eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+")),
    ("Bearer Token",       re.compile(r"(?i)bearer\s+[A-Za-z0-9\-_\.=]{20,}")),
    ("Basic Auth",         re.compile(r"(?i)authorization:\s*basic\s+[A-Za-z0-9+/=]{16,}")),
    ("Firebase URL",       re.compile(r"https://[a-z0-9\-]+\.firebaseio\.com")),
    ("Firebase Key",       re.compile(r"AAAA[A-Za-z0-9_\-]{7}:[A-Za-z0-9_\-]{140}")),
    ("Heroku API Key",     re.compile(r"(?i)heroku.{0,20}[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")),
    ("NPM Token",          re.compile(r"npm_[A-Za-z0-9]{36}")),
    ("PyPI Token",         re.compile(r"pypi-[A-Za-z0-9_\-]{50,}")),
    ("OpenAI Key",         re.compile(r"sk-[A-Za-z0-9]{20}T3BlbkFJ[A-Za-z0-9]{20}")),
    ("Anthropic Key",      re.compile(r"sk-ant-[A-Za-z0-9\-_]{80,}")),
    ("Mapbox Token",       re.compile(r"pk\.[A-Za-z0-9]{60,}\.[A-Za-z0-9]{20,}")),
    ("Facebook Token",     re.compile(r"EAACEdEose0cBA[0-9A-Za-z]+")),
    ("Twitter Bearer",     re.compile(r"AAAAAAAAAAAAAAAAAAAAA[A-Za-z0-9%]{30,}")),
    ("Cloudflare Key",     re.compile(r"(?i)cloudflare.{0,20}[a-z0-9_\-]{37}")),
    ("DigitalOcean Token", re.compile(r"dop_v1_[a-f0-9]{64}")),
    ("Shopify Token",      re.compile(r"shpat_[a-f0-9]{32}")),
    ("Square Token",       re.compile(r"sq0atp-[A-Za-z0-9_\-]{22}")),
    ("Telegram Bot",       re.compile(r"\d{8,10}:[A-Za-z0-9_\-]{35}")),
    ("Generic API Key",    re.compile(r"(?i)(?:api[_\-]?key|apikey)['\"\s:=]+([A-Za-z0-9_\-]{16,64})")),
    ("Generic Secret",     re.compile(r"(?i)(?:secret|passwd|password|pwd)['\"\s:=]+([^\s'\"<>]{8,64})")),
    ("Generic Token",      re.compile(r"(?i)(?:token|access_token)['\"\s:=]+([A-Za-z0-9_\-\.]{20,})")),
    ("Email",              re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")),
    ("Internal IP",        re.compile(r"\b(?:10|172\.(?:1[6-9]|2\d|3[01])|192\.168)(?:\.\d{1,3}){2}\b")),
    ("S3 Bucket",          re.compile(r"[a-z0-9\.\-]{3,63}\.s3(?:[\.\-][a-z0-9\-]+)?\.amazonaws\.com")),
    ("Azure Blob",         re.compile(r"https://[a-z0-9]+\.blob\.core\.windows\.net")),
    ("Mongo URI",          re.compile(r"mongodb(?:\+srv)?://[^\s'\"]+")),
    ("Postgres URI",       re.compile(r"postgres(?:ql)?://[^\s'\"]+")),
    ("MySQL URI",          re.compile(r"mysql://[^\s'\"]+")),
    ("Redis URI",          re.compile(r"redis://[^\s'\"]+")),
]

JS_ENDPOINT_PATTERNS = [
    re.compile(r"""fetch\(\s*['"`]([^'"`]+)['"`]"""),
    re.compile(r"""axios\.(?:get|post|put|delete|patch|head|options)\(\s*['"`]([^'"`]+)['"`]"""),
    re.compile(r"""\$\.(?:get|post|ajax)\(\s*['"`]([^'"`]+)['"`]"""),
    re.compile(r"""\.open\(\s*['"`][A-Z]+['"`]\s*,\s*['"`]([^'"`]+)['"`]"""),
    re.compile(r"""url\s*:\s*['"`]([^'"`]+)['"`]"""),
    re.compile(r"""['"`](/api/[^'"`\s]{2,80})['"`]"""),
    re.compile(r"""['"`](/v[0-9]+/[^'"`\s]{2,80})['"`]"""),
    re.compile(r"""['"`](https?://[^'"`\s]{4,120})['"`]"""),
]

# ══════════════════════════════════════════════════════════════════════
#  CROSS-PLATFORM TERMINAL
# ══════════════════════════════════════════════════════════════════════
def clear_screen():
    if IS_WINDOWS:
        os.system("cls")
    else:
        os.system("clear")

def term_width(default=80):
    try:
        return os.get_terminal_size().columns
    except Exception:
        return default

def cwidth():
    return min(term_width(), 96)

# ══════════════════════════════════════════════════════════════════════
#  HEX ANIMATIONS — MODERN NEON
# ══════════════════════════════════════════════════════════════════════
HEX_CHARS = "0123456789ABCDEF"

def hex_stream_row(width):
    out = []
    for _ in range(width // 5):
        b = random.choice(HEX_CHARS) + random.choice(HEX_CHARS)
        out.append(f"0x{b}")
    return " ".join(out)

def hex_rain(duration=1.4, rows=6):
    width = term_width()
    end = time.time() + duration
    print("\n" * rows, end="")
    palette = [P2, P1, M3, M2, C4, C3]
    while time.time() < end:
        sys.stdout.write(f"\033[{rows}A")
        for r in range(rows):
            depth = rows - r
            c = palette[min(depth-1, len(palette)-1)]
            sys.stdout.write(f"{c}{hex_stream_row(width)}{RS}\n")
        sys.stdout.flush()
        time.sleep(0.06)

def hex_boot_banner():
    clear_screen()
    width = cwidth()
    print()
    # top gradient rule
    line = ""
    for i in range(width):
        t = i / max(width-1, 1)
        if t < 0.33:   line += f"{C1}─"
        elif t < 0.66: line += f"{M1}─"
        else:          line += f"{P1}─"
    print(line + RS)
    print()

    # hex stream rows
    for i, c in enumerate([P2, P1, M3, M2, C3]):
        print(f"{c}{hex_stream_row(width)}{RS}")

    print()
    steps = [
        ("initializing monster core",       C1),
        ("loading signature arsenal",       C2),
        ("wiring async crawl engine",       M2),
        ("arming directory probe",          M1),
        ("mounting secret hunter",          P1),
        ("compiling endpoint miner",        M3),
        ("stamping MR HAXOR signature",     C1),
    ]
    for label, c in steps:
        dots = "." * max(2, 44 - len(label))
        print(f"  {c}●{RS}  {DW}{label}{SL}{dots}{RS} ", end="", flush=True)
        for _ in range(14):
            sys.stdout.write(f"{c}{random.choice(HEX_CHARS)}{RS}")
            sys.stdout.flush()
            time.sleep(0.012)
        print(f"  {GRN}[ok]{RS}")
        time.sleep(0.04)

    print()
    time.sleep(0.2)

def hex_pulse(label, duration=0.3):
    width = max(8, cwidth() - len(label) - 16)
    end = time.time() + duration
    while time.time() < end:
        seg = "".join(random.choice(HEX_CHARS)
                      for _ in range(min(24, width)))
        sys.stdout.write(f"\r  {C2}{label}{RS} {SL}·{RS} "
                         f"{P1}{seg}{RS}")
        sys.stdout.flush()
        time.sleep(0.05)
    # final settled rule
    seg = "─" * min(24, width)
    sys.stdout.write(f"\r  {C1}{label}{RS} {SL}·{RS} {M2}{seg}{RS}\n")
    sys.stdout.flush()

def hex_spinner_frames():
    return ["0x0","0x1","0x2","0x3","0x4","0x5","0x6","0x7",
            "0x8","0x9","0xA","0xB","0xC","0xD","0xE","0xF"]

# ══════════════════════════════════════════════════════════════════════
#  MODERN UI PRIMITIVES
# ══════════════════════════════════════════════════════════════════════
def pill(label, color):
    return f"{color}▐{RS} {BOLD}{W}{label}{RS}"

def ok(m):    print(f"  {GRN}✓{RS}  {DW}{m}{RS}")
def info(m):  print(f"  {C2}i{RS}  {DW}{m}{RS}")
def warn(m):  print(f"  {YEL}!{RS}  {DW}{m}{RS}")
def err(m):   print(f"  {RED}✗{RS}  {DW}{m}{RS}")
def step(m):  print(f"  {SL}→{RS}  {DW}{m}{RS}")
def hit(m):   print(f"  {M1}★{RS}  {W}{m}{RS}")
def saved(m): print(f"  {MN1}+{RS}  {MN2}{m}{RS}")

def rule(label=None, color=C2, width=None):
    w = width or cwidth()
    if label:
        pad = max(0, w - len(label) - 6)
        print(f"  {color}── {BOLD}{W}{label}{RS} {color}{'─'*pad}{RS}")
    else:
        print(f"  {color}{'─'*w}{RS}")

def section(t):
    print()
    hex_pulse(f"▎ {t}")

def section_end():
    print()

def banner():
    clear_screen()
    plat = ("TERMUX" if IS_TERMUX else
            "WINDOWS" if IS_WINDOWS else
            "MACOS"  if IS_MAC else
            "LINUX"  if IS_LINUX else
            "UNKNOWN")
    py = platform.python_version()
    w = cwidth()

    # top gradient rule
    line = ""
    for i in range(w):
        t = i / max(w-1, 1)
        if t < 0.33:   line += f"{C1}━"
        elif t < 0.66: line += f"{M1}━"
        else:          line += f"{P1}━"
    print(line + RS)

    print(f"""
{C1}              ███╗   ███╗██████╗     ██╗  ██╗ █████╗ ██╗  ██╗ ██████╗ ██████╗ {RS}
{M2}              ████╗ ████║██╔══██╗    ██║  ██║██╔══██╗╚██╗██╔╝██╔═══██╗██╔══██╗{RS}
{M1}              ██╔████╔██║██████╔╝    ███████║███████║ ╚███╔╝ ██║   ██║██████╔╝{RS}
{P1}              ██║╚██╔╝██║██╔══██╗    ██╔══██║██╔══██║ ██╔██╗ ██║   ██║██╔══██╗{RS}
{P2}              ██║ ╚═╝ ██║██║  ██║    ██║  ██║██║  ██║██╔╝ ██╗╚██████╔╝██║  ██║{RS}
{C4}              ╚═╝     ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝{RS}

{M2}                        ───  {C1}O R{RS}  {SL}/{RS}  {M1}O R A C L E{RS}  {SL}/{RS}  {P1}R I S E{RS}  {M2}───{RS}
""")

    print(f"  {SL}╭{'─'*(w-4)}╮{RS}")
    print(f"  {SL}│{RS}  {pill('MONSTER WEB CRACKER', C1)}   "
          f"{SL}v{VERSION} · MODERN EDITION{RS}")
    print(f"  {SL}│{RS}  {DW}deep crawler · async engine · secret hunter · "
          f"endpoint miner{RS}")
    print(f"  {SL}│{RS}")
    print(f"  {SL}│{RS}  {C2}AUTHOR{RS}  {BOLD}{W}{AUTHOR}{RS}")
    print(f"  {SL}│{RS}  {C2}SYSTEM{RS}  {DW}{plat} · python {py}{RS}")
    print(f"  {SL}╰{'─'*(w-4)}╯{RS}")
    print()

# ══════════════════════════════════════════════════════════════════════
#  SPINNER · PROGRESS
# ══════════════════════════════════════════════════════════════════════
_spin_on = False
_spin_thread = None
_spin_lock = threading.Lock()

def _spin(msg):
    frames = hex_spinner_frames()
    i = 0
    while _spin_on:
        with _spin_lock:
            print(f"\r  {C1}{frames[i%len(frames)]}{RS}  "
                  f"{DW}{msg}{RS}", end="", flush=True)
        time.sleep(0.10)
        i += 1
    with _spin_lock:
        print("\r" + " "*(len(msg)+14) + "\r", end="", flush=True)

def spin_start(m):
    global _spin_on, _spin_thread
    _spin_on = True
    _spin_thread = threading.Thread(target=_spin, args=(m,), daemon=True)
    _spin_thread.start()

def spin_stop():
    global _spin_on
    _spin_on = False
    if _spin_thread:
        _spin_thread.join()

def progress(done, total, width=28):
    pct = done / max(total, 1)
    fill = int(width * pct)
    # gradient fill
    bar = ""
    for i in range(fill):
        t = i / max(width-1, 1)
        if t < 0.33:   bar += f"{C1}█"
        elif t < 0.66: bar += f"{M1}█"
        else:          bar += f"{P1}█"
    empty = f"{SL}{'░'*(width-fill)}{RS}"
    return (f"{C2}▕{RS}{bar}{empty}{C2}▏{RS} "
            f"{W}{done}{SL}/{total}{RS} {DIM}{pct*100:>3.0f}%{RS}")

# ══════════════════════════════════════════════════════════════════════
#  HTTP ENGINE
# ══════════════════════════════════════════════════════════════════════
def build_session():
    s = requests.Session()
    retry = Retry(
        total=2, backoff_factor=0.4,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET","POST","HEAD"],
    )
    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=64,
        pool_maxsize=64,
    )
    s.mount("http://",  adapter)
    s.mount("https://", adapter)
    s.verify = False
    return s

def rand_ua():
    return random.choice(USER_AGENTS)

def base_headers(extra=None):
    h = {
        "User-Agent": rand_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "no-cache",
        "DNT": "1",
    }
    if extra:
        h.update(extra)
    return h

def fetch(session, url, method="GET", timeout=DEFAULT_TIMEOUT,
          allow_redirects=True, stream=False, extra_headers=None,
          data=None):
    try:
        return session.request(
            method, url,
            headers=base_headers(extra_headers),
            timeout=timeout,
            allow_redirects=allow_redirects,
            stream=stream, data=data,
        )
    except requests.exceptions.SSLError:
        try:
            return session.request(
                method, url,
                headers=base_headers(extra_headers),
                timeout=timeout, verify=False,
                allow_redirects=allow_redirects,
                stream=stream, data=data,
            )
        except Exception as e:
            return _fake_resp(str(e))
    except Exception as e:
        return _fake_resp(str(e))

class _FakeResp:
    def __init__(self, err):
        self.status_code = 0
        self.text = ""
        self.content = b""
        self.headers = {}
        self.url = ""
        self.error = err
        self.encoding = "utf-8"

def _fake_resp(err):
    return _FakeResp(err)

# ══════════════════════════════════════════════════════════════════════
#  URL CLASSIFICATION
# ══════════════════════════════════════════════════════════════════════
def ext_of(url):
    return os.path.splitext(urlparse(url).path)[1].lower()

def categorize(url):
    e = ext_of(url)
    if e in IMAGE_EXTS:   return "images"
    if e in SVG_EXTS:     return "svg"
    if e in FONT_EXTS:    return "fonts"
    if e in DOC_EXTS:     return "docs"
    if e in MEDIA_EXTS:   return "media"
    if e in ARCHIVE_EXTS: return "archives"
    if e == ".css":       return "css"
    if e in (".js",".mjs"): return "js"
    if e == ".map":       return "sourcemaps"
    if e in (".json",".xml",".yaml",".yml"): return "config"
    if e == ".wasm":      return "wasm"
    return "assets"

def is_html(url):
    return ext_of(url) in HTML_EXTS

def same_host(a, b):
    return urlparse(a).netloc == urlparse(b).netloc

def safe_name(url, fallback="file"):
    p = urlparse(url)
    n = os.path.basename(p.path)
    if not n or n in ("", "/"):
        n = f"{fallback}_{hashlib.md5(url.encode()).hexdigest()[:8]}"
    n = re.sub(r"[^a-zA-Z0-9._\-]", "_", n)
    return n[:100]

# ══════════════════════════════════════════════════════════════════════
#  DEEP HTML PARSER
# ══════════════════════════════════════════════════════════════════════
class DeepParser(HTMLParser):
    def __init__(self, base):
        super().__init__()
        self.base = base
        self.anchors   = set()
        self.css_links = set()
        self.js_links  = set()
        self.img_links = set()
        self.svg_links = set()
        self.bg_links  = set()
        self.srcset    = set()
        self.iframes   = set()
        self.forms     = []
        self.meta      = {}
        self.comments  = []
        self._in_script = False
        self._script_blob = []
        self._in_style = False
        self._style_blob = []
        self._cur_form = None

    def _abs(self, href):
        if not href: return None
        href = href.strip()
        if href.startswith(("javascript:","mailto:","tel:",
                            "data:","blob:","#","about:")):
            return None
        return urldefrag(urljoin(self.base, href))[0]

    def _srcset(self, ss):
        for part in ss.split(","):
            u = part.strip().split()
            if u:
                a = self._abs(u[0])
                if a: yield a

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a":
            u = self._abs(d.get("href",""))
            if u: self.anchors.add(u)
        elif tag in ("img","image"):
            u = self._abs(d.get("src",""))
            if u:
                (self.svg_links if ext_of(u) in SVG_EXTS
                 else self.img_links).add(u)
            for su in self._srcset(d.get("srcset","")):
                self.srcset.add(su)
        elif tag == "source":
            for su in self._srcset(d.get("srcset","")):
                self.srcset.add(su)
            u = self._abs(d.get("src",""))
            if u: self.srcset.add(u)
        elif tag == "link":
            rel = (d.get("rel","") or "").lower()
            u = self._abs(d.get("href",""))
            if not u: return
            if "stylesheet" in rel:
                self.css_links.add(u)
            elif "icon" in rel or "apple-touch-icon" in rel or "mask-icon" in rel:
                self.img_links.add(u)
            elif "preload" in rel and d.get("as","") in ("script","style","font","image"):
                (self.js_links if d.get("as")=="script" else
                 self.css_links if d.get("as")=="style" else
                 self.img_links).add(u)
            elif "manifest" in rel:
                self.css_links.add(u)
        elif tag == "script":
            u = self._abs(d.get("src",""))
            if u:
                self.js_links.add(u)
            else:
                self._in_script = True
                self._script_blob = []
        elif tag == "style":
            self._in_style = True
            self._style_blob = []
        elif tag == "iframe":
            u = self._abs(d.get("src",""))
            if u: self.iframes.add(u)
        elif tag == "use":
            u = self._abs(d.get("href","") or d.get("xlink:href",""))
            if u: self.svg_links.add(u)
        elif tag in ("object","embed"):
            u = self._abs(d.get("data","") or d.get("src",""))
            if u: self.img_links.add(u)
        elif tag == "meta":
            k = (d.get("name") or d.get("property") or "").lower()
            v = d.get("content","")
            if k: self.meta[k] = v
        elif tag == "form":
            self._cur_form = {
                "action": d.get("action",""),
                "method": (d.get("method","GET") or "GET").upper(),
                "inputs": [],
                "enctype": d.get("enctype",""),
            }
        elif tag == "input" and self._cur_form is not None:
            self._cur_form["inputs"].append({
                "name": d.get("name",""),
                "type": (d.get("type","text") or "text").lower(),
                "id":   d.get("id",""),
                "value": d.get("value",""),
            })
        elif tag == "textarea" and self._cur_form is not None:
            self._cur_form["inputs"].append({
                "name": d.get("name",""), "type": "textarea",
                "id": d.get("id",""), "value": "",
            })
        elif tag == "select" and self._cur_form is not None:
            self._cur_form["inputs"].append({
                "name": d.get("name",""), "type": "select",
                "id": d.get("id",""), "value": "",
            })
        style = d.get("style","")
        if style and "url(" in style:
            for m in re.finditer(r'url\(["\']?([^"\')\s]+)["\']?\)', style):
                u = self._abs(m.group(1))
                if u: self.bg_links.add(u)

    def handle_endtag(self, tag):
        if tag == "form" and self._cur_form:
            self.forms.append(self._cur_form)
            self._cur_form = None
        if tag == "script" and self._in_script:
            self._in_script = False
        if tag == "style" and self._in_style:
            self._in_style = False

    def handle_data(self, data):
        if self._in_script:
            self._script_blob.append(data)
        if self._in_style:
            self._style_blob.append(data)

    def handle_comment(self, data):
        if data.strip():
            self.comments.append(data.strip()[:500])

    def inline_scripts(self):
        return "\n".join(self._script_blob)

    def inline_styles(self):
        return "\n".join(self._style_blob)

# ══════════════════════════════════════════════════════════════════════
#  EXTRACTORS
# ══════════════════════════════════════════════════════════════════════
def css_urls(text, base):
    out = set()
    for m in re.finditer(r'url\(\s*["\']?([^"\')\s]+)["\']?\s*\)', text):
        r = m.group(1).strip()
        if r.startswith("data:"): continue
        out.add(urljoin(base, r))
    return out

def js_endpoints(text, base):
    out = set()
    for pat in JS_ENDPOINT_PATTERNS:
        for m in pat.finditer(text):
            u = m.group(1)
            if u.startswith(("http://","https://","/")):
                out.add(urljoin(base, u))
    return out

def scan_secrets(text, source):
    found = []
    for name, pat in SECRET_PATTERNS:
        for m in pat.finditer(text):
            val = m.group(0)
            if len(val) > 200:
                val = val[:200] + "..."
            found.append({"type": name, "match": val, "source": source})
    return found

def is_reflected(payload, html):
    if not html or not payload: return False
    esc = payload.replace("<","&lt;").replace(">","&gt;")
    return payload in html or esc in html

def collect_params(url):
    return list(parse_qs(urlparse(url).query, keep_blank_values=True).keys())

# ══════════════════════════════════════════════════════════════════════
#  OUTPUT FOLDER
# ══════════════════════════════════════════════════════════════════════
SUBFOLDERS = ["pages","css","js","sourcemaps","images","svg","fonts",
              "docs","media","archives","config","wasm","assets",
              "reports","raw"]

def make_out(base_url):
    host = re.sub(r"[^a-zA-Z0-9_\-]", "_",
                  urlparse(base_url).netloc.replace("www.",""))
    ts = time.strftime("%Y%m%d_%H%M%S")
    root = f"MWC_{host}_{ts}"
    for sub in SUBFOLDERS:
        os.makedirs(os.path.join(root, sub), exist_ok=True)
    return root

# ══════════════════════════════════════════════════════════════════════
#  STATE
# ══════════════════════════════════════════════════════════════════════
class State:
    def __init__(self, base):
        self.base = base
        self.host = urlparse(base).netloc
        self.folder = make_out(base)
        self.visited_pages = set()
        self.queued = set()
        self.assets = {}
        self.secrets = []
        self.endpoints = set()
        self.dir_hits = []
        self.params = set()
        self.reflections = []
        self.forms_found = []
        self.pages_info = []
        self.comments = []
        self.lock = threading.Lock()
        self.session = build_session()
        self.manifest = {
            "tool": TOOL_NAME,
            "version": VERSION,
            "author": AUTHOR,
            "target": base,
            "host": self.host,
            "started": datetime.utcnow().isoformat() + "Z",
            "ip": self._resolve_ip(),
            "platform": "termux" if IS_TERMUX else
                        "windows" if IS_WINDOWS else
                        "macos" if IS_MAC else
                        "linux",
            "pages": [], "assets": {}, "secrets": [],
            "endpoints": [], "dir_hits": [],
            "params": [], "reflections": [], "forms": [],
        }

    def _resolve_ip(self):
        try:
            return socket.gethostbyname(urlparse(self.base).hostname)
        except Exception:
            return "N/A"

    def add_secret(self, entry):
        with self.lock: self.secrets.append(entry)
    def add_endpoint(self, url):
        with self.lock: self.endpoints.add(url)
    def add_asset(self, url, cat):
        with self.lock: self.assets[url] = cat
    def add_param(self, p):
        with self.lock: self.params.add(p)

    def write(self, sub, name, content, mode="w"):
        path = os.path.join(self.folder, sub, name)
        with open(path, mode,
                  encoding="utf-8" if "b" not in mode else None,
                  errors="replace" if "b" not in mode else None) as f:
            f.write(content)
        return path

    def write_bin(self, sub, name, data):
        path = os.path.join(self.folder, sub, name)
        with open(path, "wb") as f:
            f.write(data)
        return path

# ══════════════════════════════════════════════════════════════════════
#  ROBOTS + SITEMAP
# ══════════════════════════════════════════════════════════════════════
def parse_robots(state):
    section("ROBOTS · SITEMAP")
    found_urls = set()
    r = fetch(state.session, urljoin(state.base, "/robots.txt"))
    if r.status_code == 200 and r.text:
        state.write("raw", "robots.txt", r.text)
        sitemaps  = re.findall(r"(?im)^sitemap:\s*(\S+)", r.text)
        disallowed = re.findall(r"(?im)^disallow:\s*(\S+)", r.text)
        for d in disallowed:
            if d and d != "/":
                found_urls.add(urljoin(state.base, d))
        for sm in sitemaps:
            step(f"robots → sitemap: {sm}")
            found_urls.update(parse_sitemap(state, sm))
        ok(f"robots.txt · {len(disallowed)} disallow · {len(sitemaps)} sitemap(s)")
    else:
        info("no robots.txt")

    for path in ("/sitemap.xml","/sitemap_index.xml","/sitemap-index.xml"):
        if path.endswith("_index.xml") or path.endswith("-index.xml"):
            found_urls.update(parse_sitemap(state, urljoin(state.base, path)))
    return found_urls

def parse_sitemap(state, url):
    out = set()
    r = fetch(state.session, url, timeout=15)
    if r.status_code != 200 or not r.text:
        return out
    raw = r.text
    name = safe_name(url, "sitemap") or "sitemap.xml"
    if not name.endswith(".xml"): name += ".xml"
    state.write("raw", name, raw)
    for m in re.finditer(r"<sitemap>.*?<loc>\s*([^<\s]+)\s*</loc>",
                         raw, re.S|re.I):
        out.update(parse_sitemap(state, m.group(1).strip()))
    for m in re.finditer(r"<loc>\s*([^<\s]+)\s*</loc>", raw, re.I):
        out.add(m.group(1).strip())
    return out

# ══════════════════════════════════════════════════════════════════════
#  DIRECTORY PROBE
# ══════════════════════════════════════════════════════════════════════
INTERESTING_DIR_CODES = {200, 201, 202, 204, 301, 302, 307, 308, 401, 403}

def probe_dirs(state):
    section(f"DIRECTORY PROBE · {len(DIR_WORDLIST)} PATHS")
    base = state.base.rstrip("/")
    hits = []
    done = 0
    total = len(DIR_WORDLIST)

    def probe(path):
        url = f"{base}/{path.lstrip('/')}"
        r = fetch(state.session, url, timeout=8, allow_redirects=False)
        return path, url, r

    with ThreadPoolExecutor(max_workers=MAX_DIR_WORKERS) as ex:
        futures = [ex.submit(probe, p) for p in DIR_WORDLIST]
        for fut in as_completed(futures):
            try:
                path, url, r = fut.result()
            except Exception:
                continue
            done += 1
            code = r.status_code
            size = len(r.content) if r.content else 0
            print(f"\r  {progress(done,total)}  {SL}{path[:34]:<34}{RS}",
                  end="", flush=True)
            if code in INTERESTING_DIR_CODES:
                hits.append({
                    "path": path, "url": url,
                    "code": code, "size": size,
                    "ct": r.headers.get("Content-Type",""),
                })
                with state.lock:
                    state.dir_hits.append(hits[-1])
    print()
    section_end()
    ok(f"live paths: {len(hits)}")
    return hits

# ══════════════════════════════════════════════════════════════════════
#  REFLECTION TEST
# ══════════════════════════════════════════════════════════════════════
REFLECT_MARKER = "mwc5x1337"

def test_reflection(state, url, method="GET", param=None):
    if not param: return
    q = parse_qs(urlparse(url).query, keep_blank_values=True)
    q[param] = [REFLECT_MARKER]
    new_q = urlencode(q, doseq=True)
    pu = urlunparse(urlparse(url)._replace(query=new_q))
    r = fetch(state.session, pu, timeout=10)
    if r.status_code == 200 and is_reflected(REFLECT_MARKER, r.text):
        with state.lock:
            state.reflections.append({
                "url": url, "param": param, "method": method,
                "evidence": REFLECT_MARKER,
            })

# ══════════════════════════════════════════════════════════════════════
#  PAGE PROCESSOR
# ══════════════════════════════════════════════════════════════════════
def process_page(state, url, depth):
    with state.lock:
        if url in state.visited_pages: return None
        state.visited_pages.add(url)

    r = fetch(state.session, url, timeout=DEFAULT_TIMEOUT)
    if r.status_code == 0 or r.status_code >= 500:
        return None

    ct = r.headers.get("Content-Type","")
    if "html" not in ct.lower() and r.status_code == 200 and not is_html(url):
        with state.lock:
            state.assets[url] = categorize(url)
        return None

    html = r.text or ""
    parser = DeepParser(url)
    try: parser.feed(html)
    except Exception: pass

    fn = safe_name(url, "index")
    if not fn or fn in (".",""): fn = "index.html"
    if not fn.endswith((".html",".htm",".php",".asp",".aspx",".jsp")):
        fn = fn + ".html"
    state.write("pages", fn, html)

    for s in scan_secrets(html, url):
        state.add_secret(s)

    inline_js = parser.inline_scripts()
    if inline_js:
        jn = fn.rsplit(".",1)[0] + "_inline.js"
        state.write("js", jn, inline_js)
        for s in scan_secrets(inline_js, url + " (inline-js)"):
            state.add_secret(s)
        for e in js_endpoints(inline_js, url):
            state.add_endpoint(e)
        for m in re.finditer(r"sourceMappingURL=([^\s/*]+)", inline_js):
            state.add_asset(urljoin(url, m.group(1)), "sourcemaps")

    inline_css = parser.inline_styles()
    if inline_css:
        cn = fn.rsplit(".",1)[0] + "_inline.css"
        state.write("css", cn, inline_css)
        for cu in css_urls(inline_css, url):
            state.add_asset(cu, categorize(cu))

    for f in parser.forms:
        f2 = dict(f); f2["page"] = url
        with state.lock:
            state.forms_found.append(f2)
        for inp in f["inputs"]:
            if inp["name"]:
                state.add_param(inp["name"])

    for p in collect_params(url):
        state.add_param(p)

    params = collect_params(url)
    if params:
        test_reflection(state, url, "GET", params[0])

    for fr in parser.iframes:
        if same_host(fr, state.base):
            with state.lock:
                if fr not in state.queued and fr not in state.visited_pages:
                    state.queued.add(fr)

    for a in (parser.img_links | parser.srcset | parser.bg_links |
              parser.svg_links):
        state.add_asset(a, categorize(a))
    for c in parser.css_links:
        state.add_asset(c, "css" if ext_of(c) == ".css" else categorize(c))
    for j in parser.js_links:
        state.add_asset(j, "js")
    for e in js_endpoints(html, url):
        state.add_endpoint(e)

    with state.lock:
        state.pages_info.append({
            "url": url, "file": fn, "status": r.status_code,
            "bytes": len(r.content or b""), "depth": depth,
            "server": r.headers.get("Server","?"),
            "title": parser.meta.get("og:title")
                     or parser.meta.get("title") or "",
        })

    nexts = []
    for a in parser.anchors | parser.iframes:
        if same_host(a, state.base) and a not in state.visited_pages:
            if is_html(a):
                nexts.append(a)
            else:
                state.add_asset(a, categorize(a))
    return nexts

# ══════════════════════════════════════════════════════════════════════
#  CRAWLER
# ══════════════════════════════════════════════════════════════════════
def crawl(state, seeds, max_pages=80, max_depth=4, delay=0.25):
    section("DEEP CRAWL")
    queue = deque([(u, 0) for u in seeds])
    seen = set(seeds)
    pages_done = 0

    with ThreadPoolExecutor(max_workers=MAX_PAGE_WORKERS) as ex:
        inflight = {}
        while queue or inflight:
            while (queue and len(inflight) < MAX_PAGE_WORKERS
                   and pages_done + len(inflight) < max_pages):
                u, d = queue.popleft()
                if u in state.visited_pages: continue
                inflight[ex.submit(process_page, state, u, d)] = (u, d)

            if not inflight: break

            done_any = False
            for fut in list(inflight.keys()):
                if fut.done():
                    u, d = inflight.pop(fut)
                    pages_done += 1
                    try: nexts = fut.result() or []
                    except Exception as e:
                        nexts = []; err(f"{u} — {e}")
                    print(f"  {C2}▸{RS} {SL}[{pages_done:>3}]{RS}  "
                          f"{GRN}ok{RS}  {DW}{u[:70]}{RS}")
                    if d < max_depth:
                        for n in nexts:
                            if n not in seen:
                                seen.add(n)
                                queue.append((n, d+1))
                    done_any = True
                    time.sleep(delay)
                    break
            if not done_any:
                time.sleep(0.05)

    section_end()
    ok(f"pages crawled: {pages_done}")

# ══════════════════════════════════════════════════════════════════════
#  ASSET DOWNLOADER
# ══════════════════════════════════════════════════════════════════════
def download_assets(state, delay=0.05):
    items = list(state.assets.items())
    total = len(items)
    if not total:
        info("no assets queued")
        return 0, 0

    section(f"ASSET DOWNLOAD · {total}")
    done = 0; ok_c = 0; fail_c = 0
    manifest_assets = {}

    def grab(item):
        url, cat = item
        return url, cat, fetch(state.session, url, timeout=25)

    with ThreadPoolExecutor(max_workers=MAX_ASSET_WORKERS) as ex:
        futures = [ex.submit(grab, it) for it in items]
        for fut in as_completed(futures):
            done += 1
            try: url, cat, r = fut.result()
            except Exception:
                fail_c += 1; continue
            name = safe_name(url, cat)
            print(f"\r  {progress(done,total)}  "
                  f"{SL}{cat:<10}{RS}  {DW}{name[:40]:<40}{RS}",
                  end="", flush=True)
            if r.status_code == 200 and r.content:
                state.write_bin(cat, name, r.content)
                manifest_assets.setdefault(cat, []).append({
                    "url": url, "file": name, "size": len(r.content),
                })
                if cat in ("js","css","config","sourcemaps") or name.endswith(
                        (".js",".css",".json",".xml",".map",".txt",".yaml",".yml")):
                    try:
                        text = r.content.decode("utf-8", errors="replace")
                    except Exception:
                        text = ""
                    if text:
                        for s in scan_secrets(text, url):
                            state.add_secret(s)
                        for e in js_endpoints(text, url):
                            state.add_endpoint(e)
                        for m in re.finditer(r"sourceMappingURL=([^\s/*]+)", text):
                            state.add_asset(urljoin(url, m.group(1)), "sourcemaps")
                ok_c += 1
            else:
                fail_c += 1
            time.sleep(delay)

    print()
    section_end()
    ok(f"assets saved: {ok_c}   failed: {fail_c}")
    state.manifest["assets"] = manifest_assets
    return ok_c, fail_c

# ══════════════════════════════════════════════════════════════════════
#  REPORTS
# ══════════════════════════════════════════════════════════════════════
def write_reports(state):
    section("REPORTS")

    if state.secrets:
        seen = set()
        lines = ["# Secrets Found\n"]
        for s in state.secrets:
            key = (s["type"], s["match"])
            if key in seen: continue
            seen.add(key)
            lines.append(f"- [{s['type']}] `{s['match']}`  ←  {s['source']}")
        state.write("reports", "secrets.md", "\n".join(lines))
        saved(f"reports/secrets.md · {len(seen)} unique")
        state.manifest["secrets"] = list(seen)

    if state.endpoints:
        eps = sorted(state.endpoints)
        state.write("reports", "endpoints.txt", "\n".join(eps))
        saved(f"reports/endpoints.txt · {len(eps)}")
        state.manifest["endpoints"] = eps

    if state.dir_hits:
        lines = ["# Directory Hits\n"]
        for h in sorted(state.dir_hits, key=lambda x: x["code"]):
            lines.append(f"- [{h['code']}] {h['url']}  ({h['size']}B) {h['ct']}")
        state.write("reports", "dir_hits.md", "\n".join(lines))
        saved(f"reports/dir_hits.md · {len(state.dir_hits)}")
        state.manifest["dir_hits"] = state.dir_hits

    if state.forms_found:
        lines = ["# Forms Inventory\n"]
        for f in state.forms_found:
            lines.append(f"\n## {f['page']}")
            lines.append(f"- action: `{f.get('action','')}`")
            lines.append(f"- method: `{f.get('method','GET')}`")
            for i in f.get("inputs", []):
                lines.append(f"  - {i.get('name','')} :: "
                             f"{i.get('type','')} :: {i.get('id','')}")
        state.write("reports", "forms.md", "\n".join(lines))
        saved(f"reports/forms.md · {len(state.forms_found)}")
        state.manifest["forms"] = state.forms_found

    if state.params:
        ps = sorted(state.params)
        state.write("reports", "params.txt", "\n".join(ps))
        saved(f"reports/params.txt · {len(ps)}")
        state.manifest["params"] = ps

    if state.reflections:
        lines = ["# Reflected Parameters\n"]
        for r in state.reflections:
            lines.append(f"- {r['method']} {r['url']}  param=`{r['param']}`")
        state.write("reports", "reflections.md", "\n".join(lines))
        saved(f"reports/reflections.md · {len(state.reflections)}")
        state.manifest["reflections"] = state.reflections

    if state.pages_info:
        lines = ["# Crawled Pages\n"]
        for p in state.pages_info:
            lines.append(f"- [{p['status']}] {p['url']}  →  pages/{p['file']}")
        state.write("reports", "pages.md", "\n".join(lines))

    state.manifest["finished"] = datetime.utcnow().isoformat() + "Z"
    state.manifest["pages"] = state.pages_info
    state.manifest["summary"] = {
        "pages": len(state.pages_info),
        "assets": sum(len(v) for v in state.manifest["assets"].values()),
        "secrets": len(state.manifest.get("secrets", [])),
        "endpoints": len(state.endpoints),
        "dir_hits": len(state.dir_hits),
        "forms": len(state.forms_found),
        "params": len(state.params),
        "reflections": len(state.reflections),
    }
    with open(os.path.join(state.folder, "manifest.json"),
              "w", encoding="utf-8") as f:
        json.dump(state.manifest, f, indent=2, ensure_ascii=False, default=str)
    saved("manifest.json")
    section_end()

# ══════════════════════════════════════════════════════════════════════
#  SUMMARY — MODERN CARD
# ══════════════════════════════════════════════════════════════════════
def summary_box(state):
    s = state.manifest.get("summary", {})
    w = cwidth() - 4

    def row(k, v, c=C1, icon="▸"):
        key = f"{SL}{k:<14}{RS}"
        val = f"{c}{str(v)}{RS}"
        return f"  {SL}│{RS}  {c}{icon}{RS} {key} {val}"

    print()
    print(f"  {C2}╭{'─'*(w-2)}╮{RS}")
    title = f"MONSTER WEB CRACKER  ·  v{VERSION}"
    pad = max(0, w - len(title) - 6)
    print(f"  {C2}│{RS}  {BOLD}{W}{title}{RS}  "
          f"{M2}{'R U N   C O M P L E T E'}{RS}{' '*pad}{C2}│{RS}")
    print(f"  {C2}├{'─'*(w-2)}┤{RS}")
    print(f"  {SL}│{RS}  {C2}TARGET{RS}   {W}{state.base[:w-12]}{RS}")
    print(f"  {SL}│{RS}  {C2}IP{RS}       {DW}{state.manifest['ip']}{RS}")
    print(f"  {SL}│{RS}  {C2}OUTPUT{RS}   {DW}{state.folder}{RS}")
    print(f"  {C2}├{'─'*(w-2)}┤{RS}")
    print(row("Pages",       s.get("pages",0)))
    print(row("Assets",      s.get("assets",0)))
    print(row("Endpoints",   s.get("endpoints",0),   C3, "◆"))
    print(row("Dir Hits",    s.get("dir_hits",0),    YEL, "◆"))
    print(row("Forms",       s.get("forms",0)))
    print(row("Params",      s.get("params",0)))
    print(row("Reflections", s.get("reflections",0), YEL, "◆"))
    print(row("Secrets",     s.get("secrets",0),     M1, "◆"))
    print(f"  {C2}╰{'─'*(w-2)}╯{RS}")
    print()

    rule("folder tree", C2)
    print(f"  {C1}{state.folder}/{RS}")
    for sub in SUBFOLDERS:
        p = os.path.join(state.folder, sub)
        if os.path.isdir(p):
            n = len(os.listdir(p))
            if n:
                print(f"  {SL}├──{RS} {C2}{sub:<12}{RS} {DW}{n} file(s){RS}")
    print()

# ══════════════════════════════════════════════════════════════════════
#  INTERACTIVE MENU — MODERN
# ══════════════════════════════════════════════════════════════════════
def interactive():
    hex_boot_banner()
    banner()
    while True:
        w = cwidth() - 4
        print(f"  {C2}╭{'─'*(w-2)}╮{RS}")
        print(f"  {C2}│{RS}  {BOLD}{W}NEW TARGET{RS}  "
              f"{SL}·  {DW}type a URL  ·  {SL}or {DW}exit{RS}")
        print(f"  {C2}╰{'─'*(w-2)}╯{RS}")
        try:
            raw = input(f"  {C1}❯{RS} {M1}❯{RS} {W}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n  {SL}session ended.{RS}\n")
            return
        if raw.lower() in ("exit","quit","q",""):
            print(f"\n  {M2}MR HAXOR{RS} {SL}·{RS} {DW}signing off.{RS}\n")
            return
        if not raw.startswith(("http://","https://")):
            raw = "https://" + raw

        try:
            mp = input(f"  {C2}max pages{RS} {SL}[default 60]{RS} {C1}›{RS} ").strip()
            max_pages = int(mp) if mp.isdigit() else 60
            max_pages = max(1, min(max_pages, 500))
        except (KeyboardInterrupt, EOFError):
            max_pages = 60
        try:
            md = input(f"  {C2}max depth{RS} {SL}[default 3]{RS} {C1}›{RS} ").strip()
            max_depth = int(md) if md.isdigit() else 3
            max_depth = max(1, min(max_depth, 8))
        except (KeyboardInterrupt, EOFError):
            max_depth = 3

        print()
        print(f"  {C2}╭{'─'*(w-2)}╮{RS}")
        print(f"  {C2}│{RS}  {BOLD}{W}MODULES{RS}")
        print(f"  {C2}├{'─'*(w-2)}┤{RS}")
        print(f"  {SL}│{RS}  {C1}1{RS}  {DW}full monster{SL}     · crawl + assets + secrets + dirs{RS}")
        print(f"  {SL}│{RS}  {C1}2{RS}  {DW}crawler only{SL}     · source + secrets{RS}")
        print(f"  {SL}│{RS}  {C1}3{RS}  {DW}source + assets{SL}  · crawl + download{RS}")
        print(f"  {SL}│{RS}  {C1}4{RS}  {DW}reckless{SL}         · everything, bigger scope{RS}")
        print(f"  {C2}╰{'─'*(w-2)}╯{RS}")
        try:
            ch = input(f"  {C2}choice{RS} {SL}[default 1]{RS} {C1}›{RS} ").strip() or "1"
        except (KeyboardInterrupt, EOFError):
            ch = "1"

        do_assets = ch in ("1","3","4")
        do_dirs   = ch in ("1","4")
        do_seeds  = ch in ("1","4")

        run_one(raw, max_pages, max_depth,
                do_assets=do_assets, do_dirs=do_dirs,
                do_seeds=do_seeds, reckless=(ch == "4"))
        print()

# ══════════════════════════════════════════════════════════════════════
#  SINGLE RUN
# ══════════════════════════════════════════════════════════════════════
def run_one(target, max_pages, max_depth,
            do_assets=True, do_dirs=True, do_seeds=True, reckless=False):
    state = State(target)

    section("TARGET LOCKED")
    print(f"  {C2}▸{RS} {SL}URL{RS}     {W}{target}{RS}")
    print(f"  {C2}▸{RS} {SL}IP{RS}      {DW}{state.manifest['ip']}{RS}")
    print(f"  {C2}▸{RS} {SL}OUTPUT{RS}  {DW}{state.folder}/{RS}")
    print(f"  {C2}▸{RS} {SL}SCOPE{RS}   {DW}{max_pages} pages · depth {max_depth}{RS}")
    section_end()

    seeds = {target}

    if do_seeds:
        try:
            extra = parse_robots(state)
            for e in extra:
                if same_host(e, target) and is_html(e):
                    seeds.add(e)
        except Exception as e:
            warn(f"robots/sitemap failed: {e}")

    try:
        crawl(state, seeds, max_pages=max_pages,
              max_depth=max_depth, delay=0.2 if reckless else 0.3)
    except KeyboardInterrupt:
        spin_stop(); warn("crawl interrupted")
    except Exception as e:
        err(f"crawl error: {e}")

    if do_dirs:
        try: probe_dirs(state)
        except KeyboardInterrupt: warn("dir probe interrupted")
        except Exception as e: err(f"dir probe error: {e}")

    if do_assets:
        try: download_assets(state, delay=0.02 if reckless else 0.05)
        except KeyboardInterrupt: warn("asset download interrupted")
        except Exception as e: err(f"asset error: {e}")

    write_reports(state)
    summary_box(state)

    if state.secrets:
        hit(f"SECRETS · {len(state.secrets)}  →  reports/secrets.md")
    if state.reflections:
        hit(f"REFLECTIONS · {len(state.reflections)}  →  reports/reflections.md")
    if state.dir_hits:
        hit(f"LIVE PATHS · {len(state.dir_hits)}  →  reports/dir_hits.md")
    print()

# ══════════════════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════════════════
def cli():
    p = argparse.ArgumentParser(
        prog="monster-web-cracker",
        description=f"{TOOL_NAME} v{VERSION} — {AUTHOR}",
    )
    p.add_argument("target", nargs="?", help="URL to crawl")
    p.add_argument("-p","--pages", type=int, default=60)
    p.add_argument("-d","--depth", type=int, default=3)
    p.add_argument("--no-assets", action="store_true")
    p.add_argument("--no-dirs",   action="store_true")
    p.add_argument("--no-seeds",  action="store_true")
    p.add_argument("--reckless",  action="store_true")
    p.add_argument("--no-hex",    action="store_true")
    p.add_argument("-v","--version", action="version",
                   version=f"{TOOL_NAME} {VERSION} · {AUTHOR}")
    args = p.parse_args()

    if not args.target:
        interactive()
        return

    t = args.target
    if not t.startswith(("http://","https://")):
        t = "https://" + t

    if not args.no_hex:
        hex_boot_banner()
    banner()

    run_one(
        t, args.pages, args.depth,
        do_assets=not args.no_assets,
        do_dirs=not args.no_dirs,
        do_seeds=not args.no_seeds,
        reckless=args.reckless,
    )

# ══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        spin_stop()
        print(f"\n  {YEL}interrupted.{RS}\n")
