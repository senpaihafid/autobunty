#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         A U T O S C A N                                       ║
║              Legendary Bug Bounty Automation Framework                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝
  Author   : Anas Magane
  YouTube  : Anas Education
  LinkedIn : https://ma.linkedin.com/in/anas-magane-3aa287262
  GitHub   : https://github.com/Anas-Magane
"""

import os
import sys
import json
import time
import shutil
import argparse
import subprocess
import threading
import itertools
import re
import signal
import configparser
import tempfile
import shlex
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import urllib.request
import urllib.error

# ─────────────────────────────────────────────────────────────────────────────
#  ANSI COLOR PALETTE  (hacker terminal aesthetic)
# ─────────────────────────────────────────────────────────────────────────────
class C:
    RESET       = "\033[0m"
    BOLD        = "\033[1m"
    DIM         = "\033[2m"
    UNDERLINE   = "\033[4m"
    BLINK       = "\033[5m"

    # Greens (primary hacker colour)
    G_BRIGHT    = "\033[92m"
    G_NORMAL    = "\033[32m"
    G_DIM       = "\033[2;32m"

    # Reds
    R_BRIGHT    = "\033[91m"
    R_NORMAL    = "\033[31m"

    # Yellows / Oranges
    Y_BRIGHT    = "\033[93m"
    Y_NORMAL    = "\033[33m"

    # Blues / Cyans
    B_BRIGHT    = "\033[94m"
    B_NORMAL    = "\033[34m"
    C_BRIGHT    = "\033[96m"
    C_NORMAL    = "\033[36m"

    # Magenta / Purple
    M_BRIGHT    = "\033[95m"
    M_NORMAL    = "\033[35m"

    # White / Gray
    W_BRIGHT    = "\033[97m"
    W_NORMAL    = "\033[37m"
    GRAY        = "\033[90m"

    # Backgrounds
    BG_BLACK    = "\033[40m"
    BG_GREEN    = "\033[42m"
    BG_RED      = "\033[41m"
    BG_YELLOW   = "\033[43m"
    BG_BLUE     = "\033[44m"

    @staticmethod
    def g(t):  return f"{C.G_BRIGHT}{t}{C.RESET}"
    @staticmethod
    def r(t):  return f"{C.R_BRIGHT}{t}{C.RESET}"
    @staticmethod
    def y(t):  return f"{C.Y_BRIGHT}{t}{C.RESET}"
    @staticmethod
    def b(t):  return f"{C.B_BRIGHT}{t}{C.RESET}"
    @staticmethod
    def c(t):  return f"{C.C_BRIGHT}{t}{C.RESET}"
    @staticmethod
    def m(t):  return f"{C.M_BRIGHT}{t}{C.RESET}"
    @staticmethod
    def w(t):  return f"{C.W_BRIGHT}{t}{C.RESET}"
    @staticmethod
    def dim(t):return f"{C.DIM}{t}{C.RESET}"
    @staticmethod
    def bold(t):return f"{C.BOLD}{t}{C.RESET}"
    @staticmethod
    def bg_g(t):return f"{C.BG_BLACK}{C.G_BRIGHT}{t}{C.RESET}"

# ─────────────────────────────────────────────────────────────────────────────
#  BANNER
# ─────────────────────────────────────────────────────────────────────────────
BANNER = f"""
{C.G_BRIGHT}{C.BOLD}
  ▄████████ ███    █▄      ███      ▄██████▄     ▄████████  ▄████████    ▄████████ ███▄▄▄▄   
  ███    ███ ███    ███ ▀█████████▄ ███    ███   ███    ███ ███    ███   ███    ███ ███▀▀▀██▄ 
  ███    ███ ███    ███    ▀███▀▀██ ███    ███   ███    █▀  ███    █▀    ███    ███ ███   ███ 
  ███    ███ ███    ███     ███   ▀ ███    ███   ███        ███         ▄███▄▄▄▄██▀ ███   ███ 
▀███████████ ███    ███     ███     ███    ███ ▀███████████ ███        ▀▀███▀▀▀▀▀   ███   ███ 
  ███    ███ ███    ███     ███     ███    ███          ███ ███    █▄  ▀███████████ ███   ███ 
  ███    ███ ███    ███     ███     ███    ███    ▄█    ███ ███    ███   ███    ███ ███   ███ 
  ███    █▀  ████████▀     ███▀     ▀██████▀   ▄████████▀  ████████▀   ███    ███  ▀█   █▀  
                                                                        ███    ███          
{C.RESET}
{C.G_DIM}{'─'*90}{C.RESET}
{C.G_BRIGHT}  ⚡  Legendary Bug Bounty Automation Framework  ⚡{C.RESET}
{C.GRAY}  ┌─────────────────────────────────────────────────────────────────────────────────┐{C.RESET}
{C.GRAY}  │{C.RESET}  {C.Y_BRIGHT}Author   {C.RESET}{C.GRAY}:{C.RESET}  {C.W_BRIGHT}Anas Magane{C.RESET}
{C.GRAY}  │{C.RESET}  {C.Y_BRIGHT}YouTube  {C.RESET}{C.GRAY}:{C.RESET}  {C.C_BRIGHT}Anas Education{C.RESET}
{C.GRAY}  │{C.RESET}  {C.Y_BRIGHT}LinkedIn {C.RESET}{C.GRAY}:{C.RESET}  {C.B_BRIGHT}https://ma.linkedin.com/in/anas-magane-3aa287262{C.RESET}
{C.GRAY}  │{C.RESET}  {C.Y_BRIGHT}GitHub   {C.RESET}{C.GRAY}:{C.RESET}  {C.M_BRIGHT}https://github.com/Anas-Magane{C.RESET}
{C.GRAY}  └─────────────────────────────────────────────────────────────────────────────────┘{C.RESET}
{C.G_DIM}{'─'*90}{C.RESET}
"""

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIG  (~/.autoscan/config.ini)
# ─────────────────────────────────────────────────────────────────────────────
CONFIG_DIR  = Path.home() / ".autoscan"
CONFIG_FILE = CONFIG_DIR / "config.ini"

def load_config() -> configparser.ConfigParser:
    cfg = configparser.ConfigParser()
    CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        CONFIG_DIR.chmod(0o700)
    except OSError:
        pass
    if CONFIG_FILE.exists():
        cfg.read(CONFIG_FILE)
    if "securitytrails" not in cfg:
        cfg["securitytrails"] = {"api_key": os.environ.get("SECURITYTRAILS_API_KEY", "")}
    if "general" not in cfg:
        cfg["general"] = {"speed": "3"}
    return cfg

def save_config(cfg: configparser.ConfigParser):
    CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        CONFIG_DIR.chmod(0o700)
    except OSError:
        pass
    fd = os.open(CONFIG_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        cfg.write(f)
    try:
        CONFIG_FILE.chmod(0o600)
    except OSError:
        pass

# ─────────────────────────────────────────────────────────────────────────────
#  SPEED ↔ SLEEP  MAPPING
# ─────────────────────────────────────────────────────────────────────────────
SPEED_SLEEP = {1: 3.0, 2: 1.5, 3: 0.7, 4: 0.3, 5: 0.0}

# ─────────────────────────────────────────────────────────────────────────────
#  ARGUMENT PARSER
# ─────────────────────────────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="autoscan",
        description="Legendary Bug Bounty Automation Framework by Anas Magane",
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
    )
    p.add_argument("-u", "--url",     metavar="TARGET",  help="Target domain  (e.g. anas.com)")
    p.add_argument("-h", "--header",  metavar="HEADER",  action="append", dest="headers",
                   help='Custom header  (e.g. -h "User-Agent: Autoscan")')
    p.add_argument("-s", "--speed",   metavar="1-5",     type=int, default=None,
                   help="Scan speed  1=slow … 5=fast  (default 3)")
    p.add_argument("--api-key",       metavar="KEY",     help="SecurityTrails API key (overrides config)")
    p.add_argument("--set-api-key",   metavar="KEY",     help="Save SecurityTrails API key to config & exit")
    p.add_argument("--proxy",         metavar="PROXY",   help="HTTP proxy  (e.g. http://127.0.0.1:8080)")
    p.add_argument("--headless-storage", action="store_true", help="Opt in to browser storage collection (may contain session secrets)")
    p.add_argument("--help",          action="help",     help="Show this help message and exit")
    return p

# ─────────────────────────────────────────────────────────────────────────────
#  SPINNER / PROGRESS HELPERS
# ─────────────────────────────────────────────────────────────────────────────
_spinner_active = False
_spinner_thread  = None

def _spin(msg: str):
    chars = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    global _spinner_active
    for c in itertools.cycle(chars):
        if not _spinner_active:
            break
        sys.stdout.write(f"\r  {C.G_BRIGHT}{c}{C.RESET}  {C.W_BRIGHT}{msg}{C.RESET}   ")
        sys.stdout.flush()
        time.sleep(0.08)
    sys.stdout.write("\r" + " " * (len(msg) + 12) + "\r")
    sys.stdout.flush()

def spinner_start(msg: str):
    global _spinner_active, _spinner_thread
    _spinner_active = True
    _spinner_thread = threading.Thread(target=_spin, args=(msg,), daemon=True)
    _spinner_thread.start()

def spinner_stop():
    global _spinner_active
    _spinner_active = False
    if _spinner_thread:
        _spinner_thread.join()

def progress_bar(label: str, total: int, current: int, bar_width: int = 45):
    filled  = int(bar_width * current / max(total, 1))
    empty   = bar_width - filled
    bar     = C.G_BRIGHT + "█" * filled + C.DIM + "░" * empty + C.RESET
    pct     = int(100 * current / max(total, 1))
    sys.stdout.write(f"\r  {C.Y_BRIGHT}{label}{C.RESET}  [{bar}]  {C.C_BRIGHT}{pct:3d}%{C.RESET}  {C.GRAY}({current}/{total}){C.RESET}  ")
    sys.stdout.flush()
    if current >= total:
        print()

def step_banner(number: int, title: str):
    line = "─" * 88
    print(f"\n{C.G_DIM}{line}{C.RESET}")
    print(f"  {C.BG_BLACK}{C.G_BRIGHT} STEP {number:02d} {C.RESET}  {C.W_BRIGHT}{C.BOLD}{title}{C.RESET}")
    print(f"{C.G_DIM}{line}{C.RESET}")

def ok(msg: str):   print(f"  {C.G_BRIGHT}[✔]{C.RESET}  {msg}")
def warn(msg: str): print(f"  {C.Y_BRIGHT}[!]{C.RESET}  {msg}")
def err(msg: str):  print(f"  {C.R_BRIGHT}[✘]{C.RESET}  {msg}")
def info(msg: str): print(f"  {C.B_BRIGHT}[i]{C.RESET}  {msg}")
def note(msg: str): print(f"  {C.M_BRIGHT}[★]{C.RESET}  {C.M_BRIGHT}{msg}{C.RESET}")
def found(msg:str): print(f"  {C.G_BRIGHT}[+]{C.RESET}  {C.G_BRIGHT}{msg}{C.RESET}")
def miss(msg: str): print(f"  {C.R_BRIGHT}[-]{C.RESET}  {C.R_BRIGHT}{msg}{C.RESET}")

def completed(label: str, count: int = -1):
    extra = f"  {C.C_BRIGHT}({count} items){C.RESET}" if count >= 0 else ""
    print(f"\n  {C.G_BRIGHT}✔  Completed: {C.BOLD}{label}{C.RESET}{extra}\n")

def run_cmd(cmd: str, capture=True, timeout=300) -> tuple[int, str, str]:
    """Run an internally constructed shell command; callers must quote external values with shlex.quote."""
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=capture,
            text=True, timeout=timeout
        )
        return r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired:
        return 1, "", "timeout"
    except Exception as ex:
        return 1, "", str(ex)

def tool_exists(name: str) -> bool:
    return shutil.which(name) is not None

def go_bin(name: str) -> str:
    """Return full path to a Go binary or fallback to name."""
    candidates = [
        str(Path.home() / "go" / "bin" / name),
        f"/usr/local/go/bin/{name}",
        name,
    ]
    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return name


def in_scope_url(url: str, domain: str) -> bool:
    """Allow only HTTP(S) URLs on the requested domain or its subdomains."""
    try:
        parsed = urlparse(url if "://" in url else "https://" + url)
        host = (parsed.hostname or "").lower().rstrip(".")
        # URLs eventually enter command-line tool arguments; reject shell-expansion
        # characters rather than allowing server-provided paths to reach a shell.
        if any(ch in url for ch in ('"', "'", "\\", "`", "$", "\r", "\n")):
            return False
        if parsed.scheme not in ("http", "https"):
            return False
        if not (host == domain or host.endswith("." + domain)):
            return False
        return all(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", label)
                   for label in host.split("."))
    except Exception:
        return False

def scoped_lines(path: Path, domain: str) -> list[str]:
    """Read only in-scope HTTP(S) URLs/hostnames from scanner output."""
    if not path.exists():
        return []
    results = []
    for raw in path.read_text(errors="ignore").splitlines():
        item = raw.strip()
        if not item:
            continue
        candidate = item if "://" in item else "https://" + item
        if in_scope_url(candidate, domain):
            results.append(candidate)
    return list(dict.fromkeys(results))

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 0  ─  DIRECTORY SETUP  +  REQUIREMENTS CHECK
# ─────────────────────────────────────────────────────────────────────────────
REQUIRED_TOOLS = [
    ("subfinder",  "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"),
    ("assetfinder","go install github.com/tomnomnom/assetfinder@latest"),
    ("httpx",      "go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest"),
    ("nuclei",     "go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"),
    ("ffuf",       "go install github.com/ffuf/ffuf/v2@latest"),
    ("gobuster",   "sudo apt-get install -y gobuster  OR  go install github.com/OJ/gobuster/v3@latest"),
    ("whatweb",    "sudo apt-get install -y whatweb"),
    ("arjun",      "pip3 install arjun --break-system-packages"),
    ("jq",         "sudo apt-get install -y jq"),
    ("curl",       "sudo apt-get install -y curl"),
]

def step0_setup(domain: str) -> Path:
    step_banner(0, "WORKSPACE SETUP  +  REQUIREMENTS CHECK")
    ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
    wkdir = Path(f"BugBounty_{domain}_{ts}")
    wkdir.mkdir(parents=True, exist_ok=True)
    ok(f"Workspace created  →  {C.g(str(wkdir))}")

    # subdirectories
    for sub in ["subdomains","robots","technologies","nuclei","js_secrets",
                "cookies","bruteforce","parameters","http_methods"]:
        (wkdir / sub).mkdir(exist_ok=True)

    print()
    missing = []
    for tool, install_hint in REQUIRED_TOOLS:
        # httpx special-case: use ~/go/bin/httpx
        if tool == "httpx":
            path = go_bin("httpx")
            exists = os.path.isfile(path) and os.access(path, os.X_OK)
        else:
            exists = tool_exists(tool) or (
                os.path.isfile(str(Path.home() / "go" / "bin" / tool)) and
                os.access(str(Path.home() / "go" / "bin" / tool), os.X_OK)
            )

        if exists:
            ok(f"  {C.g(tool):30s}  {C.dim('found')}")
        else:
            warn(f"  {C.y(tool):30s}  {C.r('NOT FOUND')}  →  {C.dim(install_hint)}")
            missing.append(tool)

    if missing:
        print()
        warn(f"Missing tools: {C.r(str(len(missing)))} — please install them for full coverage.")
        warn("Autoscan will skip unavailable modules and continue.")
    else:
        ok("All required tools are available!")

    completed("Workspace Setup")
    return wkdir

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 1  ─  SUBDOMAIN ENUMERATION
# ─────────────────────────────────────────────────────────────────────────────
def step1_subdomains(domain: str, wkdir: Path, st_api_key: str,
                     extra_headers: list, sleep_sec: float) -> Path:
    step_banner(1, "SUBDOMAIN ENUMERATION")
    subs_dir = wkdir / "subdomains"

    sf_out   = subs_dir / "subfinder.txt"
    af_out   = subs_dir / "assetfinder.txt"
    st_out   = subs_dir / "securitytrails.txt"
    merged   = subs_dir / "all_subs.txt"
    full_out = subs_dir / f"{domain}-full-subs.txt"
    live_out = subs_dir / f"{domain}-live-subs.txt"

    # ── subfinder ──────────────────────────────────────────────────────────
    info(f"Running {C.g('subfinder')} on {C.c(domain)} …")
    spinner_start("subfinder scanning …")
    time.sleep(sleep_sec)
    sf_bin = go_bin("subfinder")
    rc, out, _ = run_cmd(f"{sf_bin} -d {domain} -silent -o {sf_out} 2>/dev/null", timeout=180)
    spinner_stop()
    sf_count = len(sf_out.read_text(errors="ignore").splitlines()) if sf_out.exists() else 0
    ok(f"subfinder  →  {C.g(str(sf_count))} subdomains")

    # ── assetfinder ────────────────────────────────────────────────────────
    info(f"Running {C.g('assetfinder')} on {C.c(domain)} …")
    spinner_start("assetfinder scanning …")
    time.sleep(sleep_sec)
    af_bin = go_bin("assetfinder")
    run_cmd(f"{af_bin} --subs-only {domain} > {af_out} 2>/dev/null", timeout=180)
    spinner_stop()
    af_count = len(af_out.read_text(errors="ignore").splitlines()) if af_out.exists() else 0
    ok(f"assetfinder  →  {C.g(str(af_count))} subdomains")

    # ── securitytrails ─────────────────────────────────────────────────────
    info(f"Running {C.g('SecurityTrails API')} on {C.c(domain)} …")
    spinner_start("SecurityTrails querying …")
    time.sleep(sleep_sec)
    if st_api_key:
        st_cmd = (f'curl -s -H {shlex.quote("APIKEY: " + st_api_key)} '
                  f'{shlex.quote("https://api.securitytrails.com/v1/domain/" + domain + "/subdomains")} | '
                  f'jq -r {shlex.quote(".subdomains[] | . + \"." + domain + "\"")} '
                  f'> {shlex.quote(str(st_out))} 2>/dev/null')
        run_cmd(st_cmd, timeout=60)
    else:
        st_out.write_text("")
    spinner_stop()
    st_count = len(st_out.read_text(errors="ignore").splitlines()) if st_out.exists() else 0
    ok(f"SecurityTrails  →  {C.g(str(st_count))} subdomains")

    # ── merge + deduplicate ────────────────────────────────────────────────
    all_subs = set()
    for f in [sf_out, af_out, st_out]:
        if f.exists():
            for line in f.read_text(errors="ignore").splitlines():
                line = line.strip().lower()
                candidate = line.rstrip(".").lower()
                if candidate == domain or candidate.endswith("." + domain):
                    if all(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", label)
                           for label in candidate.split(".")):
                        all_subs.add(candidate)
    # also include bare names from subfinder / assetfinder
    merged_lines = sorted(all_subs)
    merged.write_text("\n".join(merged_lines) + "\n")

    # build fully-qualified list
    fqdns = set()
    for s in merged_lines:
        if s.endswith(f".{domain}") or s == domain:
            fqdns.add(s)
        else:
            fqdns.add(f"{s}.{domain}")
    full_out.write_text("\n".join(sorted(fqdns)) + "\n")
    total_unique = len(fqdns)

    ok(f"Merged + deduplicated  →  {C.g(str(total_unique))} unique subdomains")
    print()

    # ── live probe + status codes (single httpx run) ───────────────────────
    info(f"Probing live subdomains with {C.g('httpx')} …")
    httpx_bin = go_bin("httpx")
    spinner_start("httpx probing live hosts …")
    time.sleep(sleep_sec)
    rc, raw, _ = run_cmd(
        f"{httpx_bin} -l {full_out} -status-code -silent -no-color 2>/dev/null",
        timeout=600
    )
    spinner_stop()

    STATUS_COLORS = {
        "200": C.G_BRIGHT, "201": C.G_BRIGHT, "204": C.G_BRIGHT,
        "301": C.Y_BRIGHT, "302": C.Y_BRIGHT, "303": C.Y_BRIGHT, "307": C.Y_BRIGHT,
        "401": C.M_BRIGHT, "403": C.M_BRIGHT,
        "404": C.R_BRIGHT,
        "500": C.R_BRIGHT, "503": C.R_BRIGHT,
    }
    STATUS_LABELS = {
        "200":"OK","201":"Created","204":"No Content",
        "301":"Redirect","302":"Redirect","303":"Redirect","307":"Redirect",
        "401":"Unauthorized","403":"Forbidden","404":"Not Found",
        "500":"Server Error","503":"Unavailable",
    }

    # single-pass parse: collect live URLs + buckets, then display
    live_urls: list[str] = []
    buckets: dict[str, list] = {}
    parsed: list[tuple[str, str]] = []
    for line in raw.strip().splitlines():
        m = re.search(r'(\S+)\s+\[(\d{3})\]', line)
        if m:
            url_s, code = m.group(1), m.group(2)
            live_urls.append(url_s)
            buckets.setdefault(code, []).append(url_s)
            parsed.append((url_s, code))

    live_out.write_text("\n".join(live_urls) + "\n")
    live_count = len(live_urls)

    print(f"\n  {C.G_BRIGHT}{'━'*60}{C.RESET}")
    print(f"  {C.W_BRIGHT}  You have {C.G_BRIGHT}{C.BOLD}{live_count}{C.RESET} {C.W_BRIGHT}live subdomains{C.RESET}")
    print(f"  {C.C_BRIGHT}  Hmm … let's check each subdomain 🔍{C.RESET}")
    print(f"  {C.G_BRIGHT}{'━'*60}{C.RESET}\n")

    total_l = len(parsed)
    for idx, (url_s, code) in enumerate(parsed):
        progress_bar("Classifying status codes", total_l, idx + 1)
        time.sleep(0.01)
        col = STATUS_COLORS.get(code, C.W_BRIGHT)
        lbl = STATUS_LABELS.get(code, "")
        print(f"  {C.C_BRIGHT}{url_s:55s}{C.RESET}  {col}===>{C.RESET}  "
              f"{col}{code} {lbl}{C.RESET}")

    # write per-status files
    for code, urls in buckets.items():
        (subs_dir / f"{code}.txt").write_text("\n".join(urls) + "\n")
        ok(f"Saved {C.g(str(len(urls)))} URLs with status {C.y(code)}  →  {C.dim(f'subdomains/{code}.txt')}")

    completed("Subdomain Enumeration", live_count)

    # ── redirect follow (1b) ───────────────────────────────────────────────
    redirect_urls = buckets.get("301", []) + buckets.get("302", []) + \
                    buckets.get("303", []) + buckets.get("307", [])
    if redirect_urls:
        step1b_redirect_follow(domain, wkdir, redirect_urls, extra_headers, sleep_sec)

    return live_out


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 1b  ─  REDIRECT CHAIN FOLLOW
# ─────────────────────────────────────────────────────────────────────────────
def step1b_redirect_follow(domain: str, wkdir: Path, redirect_urls: list,
                            extra_headers: list, sleep_sec: float):
    """Follow 301/302/303/307 redirects, print chains, save redirects.md."""

    subs_dir     = wkdir / "subdomains"
    redirect_md  = subs_dir / "redirects.md"
    header_args  = " ".join(f'-H "{h}"' for h in (extra_headers or []))

    REDIR_CODES  = {"301", "302", "303", "307", "308"}
    CODE_COLOR   = {
        "200": C.G_BRIGHT, "201": C.G_BRIGHT,
        "301": C.Y_BRIGHT, "302": C.Y_BRIGHT, "303": C.Y_BRIGHT,
        "307": C.Y_BRIGHT, "308": C.Y_BRIGHT,
        "403": C.M_BRIGHT, "404": C.R_BRIGHT,
        "500": C.R_BRIGHT,
    }
    CODE_LABEL   = {
        "200": "OK",          "201": "Created",
        "301": "Moved",       "302": "Found",
        "303": "See Other",   "307": "Temp Redirect",
        "308": "Perm Redirect","403": "Forbidden",
        "404": "Not Found",   "500": "Server Error",
    }

    print(f"\n  {C.Y_BRIGHT}{'━'*60}{C.RESET}")
    print(f"  {C.W_BRIGHT}  Following {C.Y_BRIGHT}{len(redirect_urls)}{C.W_BRIGHT}"
          f" redirect(s) detected 🔀{C.RESET}")
    print(f"  {C.Y_BRIGHT}{'━'*60}{C.RESET}\n")

    md_lines  = [f"# Redirect Chains — {domain}\n\n"]
    total     = len(redirect_urls)
    MAX_HOPS  = 8   # safety cap per chain

    def _get_status_and_location(url: str) -> tuple[str, str]:
        """Return (status_code, location_header_or_empty)."""
        rc, out, _ = run_cmd(
            f'curl -s -o /dev/null -w "%{{http_code}}|||%{{redirect_url}}" '
            f'{header_args} --max-time 10 --max-redirs 0 "{url}"',
            timeout=15
        )
        parts    = out.strip().split("|||")
        code     = parts[0].strip() if parts else "000"
        location = parts[1].strip() if len(parts) > 1 else ""

        # fallback: parse Location header manually if curl redirect_url empty
        if not location and code in REDIR_CODES:
            rc2, hdr_out, _ = run_cmd(
                f'curl -s -I {header_args} --max-time 10 --max-redirs 0 "{url}" '
                f'2>/dev/null | grep -i "^location:"',
                timeout=15
            )
            m = re.search(r'(?i)location:\s*(\S+)', hdr_out)
            if m:
                location = m.group(1).strip()

        return code, location

    def _resolve_location(origin_url: str, location: str) -> str:
        """Turn a relative Location into an absolute URL."""
        if location.startswith("http://") or location.startswith("https://"):
            return location
        parsed = urlparse(origin_url)
        base   = f"{parsed.scheme}://{parsed.netloc}"
        if location.startswith("/"):
            return f"{base}{location}"
        # relative path
        path_base = "/".join(parsed.path.split("/")[:-1])
        return f"{base}{path_base}/{location}"

    for idx, start_url in enumerate(redirect_urls):
        progress_bar("Following redirects", total, idx + 1)
        host  = urlparse(start_url).netloc or start_url
        chain = [start_url]
        chain_display: list[tuple[str, str, str]] = []  # (url, code, label)
        current   = start_url
        hop       = 0
        final_url = start_url

        while hop < MAX_HOPS:
            code, location = _get_status_and_location(current)
            lbl  = CODE_LABEL.get(code, f"HTTP {code}")
            chain_display.append((current, code, lbl))

            if code not in REDIR_CODES or not location:
                final_url = current
                break

            next_url = _resolve_location(current, location)
            chain.append(next_url)
            current = next_url
            hop    += 1
            time.sleep(sleep_sec * 0.15)

        # ── print the full chain ───────────────────────────────────────────
        print(f"\n  {C.C_BRIGHT}{'─'*64}{C.RESET}")
        for step_i, (u, code, lbl) in enumerate(chain_display):
            col     = CODE_COLOR.get(code, C.W_BRIGHT)
            is_last = (step_i == len(chain_display) - 1)
            arrow   = f"{C.G_DIM}└─►{C.RESET}" if is_last else f"{C.Y_BRIGHT}├─►{C.RESET}"

            if code in REDIR_CODES:
                next_u = chain[step_i + 1] if step_i + 1 < len(chain) else "?"
                print(f"  {arrow}  {C.W_BRIGHT}{u}{C.RESET}")
                print(f"        {col}{code} {lbl}{C.RESET}  {C.GRAY}→ redirect →{C.RESET}  "
                      f"{C.Y_BRIGHT}{next_u}{C.RESET}")
            else:
                print(f"  {arrow}  {C.W_BRIGHT}{u}{C.RESET}")
                print(f"        {col}{code} {lbl}{C.RESET}")

        # ── markdown ──────────────────────────────────────────────────────
        md_lines.append(f"\n## {host}\n\n")
        md_lines.append("```\n")
        for step_i, (u, code, lbl) in enumerate(chain_display):
            prefix = "└──" if step_i == len(chain_display)-1 else "├──"
            if code in REDIR_CODES and step_i + 1 < len(chain):
                md_lines.append(f"{prefix} {u}\n     {code} {lbl}  →  {chain[step_i+1]}\n")
            else:
                md_lines.append(f"{prefix} {u}\n     {code} {lbl}\n")
        md_lines.append("```\n")

        time.sleep(sleep_sec * 0.2)

    print()
    redirect_md.write_text("".join(md_lines))
    ok(f"Redirect chains saved  →  {C.g('subdomains/redirects.md')}")
    completed("Redirect Follow", len(redirect_urls))

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 2  ─  ROBOTS.TXT
# ─────────────────────────────────────────────────────────────────────────────
def step2_robots(domain: str, wkdir: Path, live_out: Path,
                 extra_headers: list, sleep_sec: float):
    step_banner(2, "ROBOTS.TXT DISCOVERY")
    robots_dir  = wkdir / "robots"
    robots_md   = robots_dir / "robots.md"

    if not live_out.exists():
        err("No live subdomains file found — skipping robots.txt check.")
        return

    subs = scoped_lines(live_out, domain)
    total = len(subs)
    md_lines = [f"# robots.txt Results — {domain}\n\n"]

    header_args = " ".join(f"-H {shlex.quote(h)}" for h in (extra_headers or []))

    for idx, sub in enumerate(subs):
        progress_bar("robots.txt scan", total, idx + 1)
        url = sub if sub.startswith("http") else f"https://{sub}"
        robots_url = url.rstrip("/") + "/robots.txt"

        rc, out, _ = run_cmd(
            f'curl -s -o /dev/null -w "%{{http_code}}" {header_args} --max-time 10 "{robots_url}"',
            timeout=20
        )
        code = out.strip()

        if code == "200":
            rc2, body, _ = run_cmd(
                f'curl -s --max-time 10 {header_args} "{robots_url}"',
                timeout=20
            )
            host = urlparse(url).netloc or url
            found(f"{C.c(host):55s}  ====>  robots.txt {C.g('[+] FOUND')}  →  {C.dim('robots/'+ host +'.txt')}")
            per_file = robots_dir / f"{host}.txt"
            per_file.write_text(body)
            md_lines.append(f"## {host}\n\n```\n{body}\n```\n\n")
        else:
            host = urlparse(url).netloc or url
            miss(f"{C.dim(host):55s}  ====>  robots.txt {C.r('[-] NOT FOUND')}  skip")
            md_lines.append(f"## {host}\n\n_robots.txt not found (HTTP {code})_\n\n")

        time.sleep(sleep_sec * 0.3)

    robots_md.write_text("".join(md_lines))
    ok(f"Full robots.txt report  →  {C.g('robots/robots.md')}")
    completed("robots.txt Discovery")

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 3  ─  TECHNOLOGIES
# ─────────────────────────────────────────────────────────────────────────────
def step3_technologies(domain: str, wkdir: Path, live_out: Path,
                       extra_headers: list, sleep_sec: float):
    step_banner(3, "TECHNOLOGY FINGERPRINTING")
    tech_dir = wkdir / "technologies"
    tech_md  = tech_dir / "technology.md"

    if not live_out.exists():
        err("No live subdomains file — skipping technologies.")
        return

    if not tool_exists("whatweb"):
        warn("whatweb not found — skipping technology fingerprinting.")
        return

    subs  = scoped_lines(live_out, domain)
    total = len(subs)
    md_lines = [f"# Technology Fingerprinting — {domain}\n\n"]

    for idx, sub in enumerate(subs):
        progress_bar("whatweb scanning", total, idx + 1)
        url = sub if sub.startswith("http") else f"https://{sub}"
        rc, out, _ = run_cmd(f'whatweb --no-errors -q "{url}" 2>/dev/null', timeout=30)
        host = urlparse(url).netloc or url
        ok(f"{C.c(host):55s}  →  {C.y(out.strip()[:80])}")
        md_lines.append(f"## {host}\n\n```\n{out.strip()}\n```\n\n")
        time.sleep(sleep_sec * 0.2)

    # wappalyzer note
    note_line = (
        "\n\n---\n"
        "## ⚠️  Manual Action Required\n\n"
        "> **PLEASE USE WAPPALYZER** to see the full versions and technologies manually.\n"
        "> Install the browser extension: https://www.wappalyzer.com/apps/\n"
    )
    md_lines.append(note_line)
    tech_md.write_text("".join(md_lines))

    note("PLEASE USE WAPPALYZER TO SEE THE VERSIONS AND TECHNOLOGIES MANUALLY")
    ok(f"Technology report  →  {C.g('technologies/technology.md')}")
    completed("Technology Fingerprinting")

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 4  ─  NUCLEI SCAN  (CVEs only)
# ─────────────────────────────────────────────────────────────────────────────
def step4_nuclei(domain: str, wkdir: Path, live_out: Path, sleep_sec: float):
    step_banner(4, "NUCLEI VULNERABILITY SCAN  (CVEs)")
    ndir = wkdir / "nuclei"

    nuclei_bin = go_bin("nuclei")
    if not (os.path.isfile(nuclei_bin) and os.access(nuclei_bin, os.X_OK)) and not tool_exists("nuclei"):
        warn("nuclei not found — skipping CVE scan.")
        return

    if not live_out.exists():
        err("No live subdomains file — skipping nuclei.")
        return

    info(f"Running nuclei CVE templates on all live subdomains …")
    out_file = ndir / "nuclei-cves.txt"
    spinner_start("nuclei scanning for CVEs (this may take a while) …")
    time.sleep(sleep_sec)

    nbin = nuclei_bin if os.path.isfile(nuclei_bin) else "nuclei"
    rc, out, _ = run_cmd(
        f'{nbin} -l {live_out} -t cves/ -o {out_file} -silent 2>/dev/null',
        timeout=1800
    )
    spinner_stop()

    if out_file.exists() and out_file.stat().st_size > 0:
        hits = out_file.read_text(errors="ignore").strip().splitlines()
        found(f"Nuclei found {C.r(str(len(hits)))} potential CVEs!")
        for h in hits[:30]:
            print(f"    {C.R_BRIGHT}  ⚡  {h}{C.RESET}")
        if len(hits) > 30:
            warn(f"  … and {len(hits)-30} more. See nuclei/nuclei-cves.txt")
    else:
        ok("No CVEs detected by nuclei (or scan produced no output).")

    completed("Nuclei CVE Scan")

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 5  ─  HTTP METHODS  (OPTIONS / TRACE / GET↔POST)
# ─────────────────────────────────────────────────────────────────────────────
def step5_http_methods(domain: str, wkdir: Path, live_out: Path,
                       extra_headers: list, sleep_sec: float):
    step_banner(5, "HTTP METHODS CHECK  (OPTIONS / TRACE / Method Switching)")
    mdir     = wkdir / "http_methods"
    meth_md  = mdir  / "http_methods.md"

    if not live_out.exists():
        err("No live subdomains — skipping HTTP methods check.")
        return

    subs  = scoped_lines(live_out, domain)
    total = len(subs)
    header_args = " ".join(f"-H {shlex.quote(h)}" for h in (extra_headers or []))
    md_lines = [f"# HTTP Methods Analysis — {domain}\n\n"]

    METHOD_COLORS = {
        "200": C.G_BRIGHT, "204": C.G_BRIGHT,
        "301": C.Y_BRIGHT, "302": C.Y_BRIGHT,
        "403": C.M_BRIGHT, "404": C.R_BRIGHT,
        "405": C.R_BRIGHT, "500": C.R_BRIGHT,
    }

    for idx, sub in enumerate(subs):
        progress_bar("HTTP method probing", total, idx + 1)
        url = sub if sub.startswith("http") else f"https://{sub}"
        host = urlparse(url).netloc or url
        md_lines.append(f"\n## {host}\n\n```\nChanging Methods ::::::::::::::\n")
        print(f"\n  {C.C_BRIGHT}{'━'*60}{C.RESET}")
        print(f"  {C.W_BRIGHT}  Changing Methods  ::::::::::::::  {C.c(host)}{C.RESET}")

        # GET / POST / OPTIONS
        for method in ["GET", "POST", "OPTIONS"]:
            rc, code_out, _ = run_cmd(
                f'curl -s -o /dev/null -w "%{{http_code}}" -X {method} {header_args} --max-time 10 "{url}"',
                timeout=20
            )
            code  = code_out.strip()
            col   = METHOD_COLORS.get(code, C.W_BRIGHT)
            label = f"HTTP {code}"

            if method == "OPTIONS":
                # also fetch Allow header
                rc2, hdr_out, _ = run_cmd(
                    f'curl -s -I -X OPTIONS {header_args} --max-time 10 "{url}" 2>/dev/null | grep -i "allow:"',
                    timeout=20
                )
                allowed = hdr_out.strip() or "N/A"
                print(f"  {C.Y_BRIGHT}  OPTIONS{C.RESET}  ======  Methods allowed: {C.g(allowed)}")
                md_lines.append(f"  OPTIONS  =>  {code}  |  {allowed}\n")
            else:
                print(f"  {C.Y_BRIGHT}  {method:6s}{C.RESET}  ======  {col}{label}{C.RESET}")
                md_lines.append(f"  {method:6s}  =>  {code}\n")
            time.sleep(0.1)

        # TRACE test
        rc, trace_out, _ = run_cmd(
            f'curl -s -o /dev/null -w "%{{http_code}}" -X TRACE {header_args} --max-time 10 "{url}"',
            timeout=20
        )
        trace_code = trace_out.strip()
        if trace_code == "200":
            warn(f"  TRACE enabled on {C.r(host)}  ← POTENTIAL VULNERABILITY!")
            md_lines.append(f"  TRACE    =>  {trace_code}  ⚠️  TRACE ENABLED — potential XST vulnerability!\n")
        else:
            ok(f"  TRACE blocked on {C.dim(host)}  ({trace_code})")
            md_lines.append(f"  TRACE    =>  {trace_code}  (blocked)\n")
        md_lines.append("```\n")
        time.sleep(sleep_sec * 0.3)

    meth_md.write_text("".join(md_lines))
    ok(f"HTTP methods report  →  {C.g('http_methods/http_methods.md')}")
    completed("HTTP Methods Check")

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 6  ─  COOKIE & STORAGE DUMP
# ─────────────────────────────────────────────────────────────────────────────
def step6_cookies(domain: str, wkdir: Path, live_out: Path,
                  extra_headers: list, sleep_sec: float,
                  use_headless: bool = True):
    step_banner(6, "COOKIE & STORAGE DUMP")
    cdir     = wkdir / "cookies"
    cook_md  = cdir  / "cookies.md"

    if not live_out.exists():
        err("No live subdomains — skipping cookie dump.")
        return

    subs  = scoped_lines(live_out, domain)
    total = len(subs)
    header_args = " ".join(f"-H {shlex.quote(h)}" for h in (extra_headers or []))
    md_lines = [f"# Cookies & Storage Dump — {domain}\n\n"]

    for idx, sub in enumerate(subs):
        progress_bar("Cookie extraction", total, idx + 1)
        url  = sub if sub.startswith("http") else f"https://{sub}"
        host = urlparse(url).netloc or url

        # ── via curl Set-Cookie header ─────────────────────────────────────
        rc, hdr_out, _ = run_cmd(
            f'curl -s -I {header_args} --max-time 10 "{url}" 2>/dev/null | grep -i "set-cookie:"',
            timeout=20
        )
        cookies_found = hdr_out.strip()

        if cookies_found:
            found(f"{C.c(host):55s}  =====  Cookies detected  →  {C.g('cookies/' + host + '_cookies.txt')}")
            per_file = cdir / f"{host}_cookies.txt"
            per_file.write_text(f"# Cookies from HTTP headers\n{cookies_found}\n")
            md_lines.append(f"## {host}\n\n### HTTP Header Cookies\n\n```\n{cookies_found}\n```\n\n")
        else:
            miss(f"{C.dim(host):55s}  =====  No cookies in response headers")
            md_lines.append(f"## {host}\n\n_No cookies detected in HTTP response headers._\n\n")

        # ── headless browser (playwright) ──────────────────────────────────
        if use_headless and tool_exists("python3"):
            playwright_script = f"""
import asyncio, json, sys
try:
    from playwright.async_api import async_playwright
    async def run():
        async with async_playwright() as p:
            b = await p.chromium.launch(headless=True)
            page = await b.new_page()
            try:
                await page.goto("{url}", timeout=15000, wait_until="domcontentloaded")
                cookies = await page.context.cookies()
                ls = await page.evaluate("() => {{try{{return JSON.stringify(localStorage)}}catch(e){{return '{{}}'}}}}")
                ss = await page.evaluate("() => {{try{{return JSON.stringify(sessionStorage)}}catch(e){{return '{{}}'}}}}")
                print("COOKIES:" + json.dumps(cookies))
                print("LOCALSTORAGE:" + ls)
                print("SESSIONSTORAGE:" + ss)
            except: pass
            await b.close()
    asyncio.run(run())
except Exception as ex:
    print("ERROR:" + str(ex))
"""
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as _tmp:
                _tmp.write(playwright_script)
                _tmp_path = Path(_tmp.name)
            rc2, pw_out, _ = run_cmd(f"python3 {_tmp_path}", timeout=30)
            _tmp_path.unlink(missing_ok=True)

            if pw_out and "COOKIES:" in pw_out:
                per_file = cdir / f"{host}_browser.txt"
                per_file.write_text(pw_out)
                md_lines.append(f"### Browser Storage (Playwright)\n\n```\n{pw_out[:2000]}\n```\n\n")
                ok(f"  {C.g('Browser cookies/storage')} saved for {C.c(host)}")

        time.sleep(sleep_sec * 0.2)

    cook_md.write_text("".join(md_lines))
    ok(f"Cookies report  →  {C.g('cookies/cookies.md')}")
    completed("Cookie & Storage Dump")

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 7  ─  DIRECTORY BRUTEFORCE  (ffuf + gobuster) — PARALLEL OPTIMIZED
# ─────────────────────────────────────────────────────────────────────────────

# Wordlist priority order: small → medium → fallback
WORDLIST_BIG    = "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"
WORDLIST_SMALL  = "/usr/share/wordlists/dirb/common.txt"
WORDLIST_RAFT_S = "/usr/share/seclists/Discovery/Web-Content/raft-small-directories.txt"
WORDLIST_RAFT_M = "/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt"

# Status codes worth bruteforcing — everything else is skipped
BRUTEFORCE_INTERESTING = {"200", "201", "301", "302", "403"}

# Workers: more workers = more parallel subdomains
BRUTEFORCE_WORKERS = 3

# Per-speed ffuf thread counts (inside one ffuf process)
FFUF_THREADS = {1: 10, 2: 20, 3: 40, 4: 80, 5: 150}

# Per-speed gobuster thread counts
GOB_THREADS = {1: 5, 2: 10, 3: 20, 4: 40, 5: 80}

# Per-speed request delay injected into ffuf (-p flag, seconds)
FFUF_DELAY = {1: "0.3-0.8", 2: "0.1-0.3", 3: "0", 4: "0", 5: "0"}

# A print lock so parallel workers don't garble each other
_bf_print_lock = threading.Lock()

def _bf_log(msg: str):
    """Thread-safe print for bruteforce workers."""
    with _bf_print_lock:
        print(msg)

def _pick_wordlist() -> tuple[str | None, str | None]:
    """
    Return (small_wl, big_wl).
    small_wl  → used first pass (fast)
    big_wl    → used only if small pass finds hits
    Returns None for paths that don't exist.
    """
    small = next((p for p in [WORDLIST_RAFT_S, WORDLIST_SMALL] if os.path.isfile(p)), None)
    big   = next((p for p in [WORDLIST_RAFT_M, WORDLIST_BIG]   if os.path.isfile(p)), None)
    return small, big

def _ffuf_scan(url: str, wordlist: str, out_file: Path,
               header_args: str, speed: int) -> list[dict]:
    """Run ffuf and return list of result dicts."""
    ffuf_b   = go_bin("ffuf")
    threads  = FFUF_THREADS.get(speed, 40)
    delay    = FFUF_DELAY.get(speed, "0")
    delay_flag = f"-p {delay}" if delay != "0" else ""

    run_cmd(
        f'{ffuf_b} -u {url}/FUZZ -w {wordlist} {header_args} '
        f'-mc 200,201,204,301,302,403 -t {threads} {delay_flag} '
        f'-o {out_file} -of json -s 2>/dev/null',
        timeout=300
    )
    if out_file.exists() and out_file.stat().st_size > 5:
        try:
            data = json.loads(out_file.read_text(errors="ignore"))
            return data.get("results", [])
        except Exception:
            return []
    return []

def _gobuster_scan(url: str, wordlist: str, out_file: Path,
                   header_args: str, speed: int) -> list[str]:
    """Run gobuster and return list of found lines."""
    gob_b   = go_bin("gobuster")
    threads = GOB_THREADS.get(speed, 20)

    run_cmd(
        f'{gob_b} dir -u {url} -w {wordlist} {header_args} '
        f'-t {threads} -o {out_file} -q --no-error 2>/dev/null',
        timeout=300
    )
    if out_file.exists() and out_file.stat().st_size > 5:
        return out_file.read_text(errors="ignore").strip().splitlines()
    return []

def _bruteforce_one(task: dict) -> dict:
    """
    Worker function — bruteforce a single subdomain.
    task keys: url, host, bdir, small_wl, big_wl, header_args_ffuf,
               header_args_gob, has_ffuf, has_gobust, speed, sleep_sec,
               status_code, idx, total
    Returns result dict with summary info.
    """
    url          = task["url"]
    host         = task["host"]
    bdir         = task["bdir"]
    small_wl     = task["small_wl"]
    big_wl       = task["big_wl"]
    hdr_ffuf     = task["header_args_ffuf"]
    hdr_gob      = task["header_args_gob"]
    has_ffuf     = task["has_ffuf"]
    has_gobust   = task["has_gobust"]
    speed        = task["speed"]
    sleep_sec    = task["sleep_sec"]
    code         = task["status_code"]
    idx          = task["idx"]
    total        = task["total"]

    result = {"host": host, "ffuf_hits": 0, "gob_hits": 0, "skipped": False, "error": None}

    # ── Filter: only interesting status codes ──────────────────────────────
    if code not in BRUTEFORCE_INTERESTING:
        result["skipped"] = True
        _bf_log(f"  {C.GRAY}[SKIP]{C.RESET}  {C.dim(host):55s}  status {C.y(code)}  (not interesting)")
        return result

    _bf_log(f"\n  {C.G_BRIGHT}[{idx+1}/{total}]{C.RESET}  {C.C_BRIGHT}Bruteforcing{C.RESET}  "
            f"{C.c(host)}  {C.dim('['+code+']')}")

    ffuf_hits_total = 0
    gob_hits_total  = 0

    # ── PHASE 1: small wordlist first ─────────────────────────────────────
    if small_wl:
        if has_ffuf:
            out_f1 = bdir / f"{host}_ffuf_small.json"
            hits1  = _ffuf_scan(url, small_wl, out_f1, hdr_ffuf, speed)
            ffuf_hits_total += len(hits1)
            if hits1:
                _bf_log(f"    {C.G_BRIGHT}[ffuf-small]{C.RESET}  {C.g(str(len(hits1)))} paths  on  {C.c(host)}")
                for h in hits1[:8]:
                    path  = h.get("input", {}).get("FUZZ", "?")
                    scode = h.get("status", 0)
                    col   = C.G_BRIGHT if str(scode) in {"200","201"} else C.Y_BRIGHT
                    _bf_log(f"      {col}  /{path:<35s}  [{scode}]{C.RESET}")

        if has_gobust:
            out_g1 = bdir / f"{host}_gobuster_small.txt"
            lines1 = _gobuster_scan(url, small_wl, out_g1, hdr_gob, speed)
            gob_hits_total += len(lines1)
            if lines1:
                _bf_log(f"    {C.B_BRIGHT}[gob-small]{C.RESET}   {C.g(str(len(lines1)))} paths  on  {C.c(host)}")

    # ── PHASE 2: big wordlist ONLY if phase 1 found something ─────────────
    phase1_found = ffuf_hits_total + gob_hits_total
    if phase1_found > 0 and big_wl and big_wl != small_wl:
        _bf_log(f"    {C.M_BRIGHT}[★]{C.RESET}  Phase 1 found {C.g(str(phase1_found))} hits on "
                f"{C.c(host)} — escalating to {C.y('BIG wordlist')} …")

        time.sleep(sleep_sec * 0.5)   # brief cooldown before escalating

        if has_ffuf:
            out_f2 = bdir / f"{host}_ffuf_big.json"
            hits2  = _ffuf_scan(url, big_wl, out_f2, hdr_ffuf, speed)
            ffuf_hits_total += len(hits2)
            if hits2:
                _bf_log(f"    {C.G_BRIGHT}[ffuf-big]{C.RESET}    {C.g(str(len(hits2)))} paths  on  {C.c(host)}")
                for h in hits2[:15]:
                    path  = h.get("input", {}).get("FUZZ", "?")
                    scode = h.get("status", 0)
                    col   = C.G_BRIGHT if str(scode) in {"200","201"} else C.Y_BRIGHT
                    _bf_log(f"      {col}  /{path:<35s}  [{scode}]{C.RESET}")

        if has_gobust:
            out_g2 = bdir / f"{host}_gobuster_big.txt"
            lines2 = _gobuster_scan(url, big_wl, out_g2, hdr_gob, speed)
            gob_hits_total += len(lines2)
            if lines2:
                _bf_log(f"    {C.B_BRIGHT}[gob-big]{C.RESET}     {C.g(str(len(lines2)))} paths  on  {C.c(host)}")
    elif phase1_found == 0 and small_wl:
        _bf_log(f"    {C.GRAY}  → no hits on small wordlist — skipping big wordlist for {host}{C.RESET}")

    # ── Fallback: no small wordlist — run big directly ─────────────────────
    elif not small_wl and big_wl:
        if has_ffuf:
            out_fb = bdir / f"{host}_ffuf.json"
            hitsb  = _ffuf_scan(url, big_wl, out_fb, hdr_ffuf, speed)
            ffuf_hits_total += len(hitsb)
            if hitsb:
                _bf_log(f"    {C.G_BRIGHT}[ffuf]{C.RESET}  {C.g(str(len(hitsb)))} paths  on  {C.c(host)}")
        if has_gobust:
            out_gb = bdir / f"{host}_gobuster.txt"
            linesb = _gobuster_scan(url, big_wl, out_gb, hdr_gob, speed)
            gob_hits_total += len(linesb)

    result["ffuf_hits"] = ffuf_hits_total
    result["gob_hits"]  = gob_hits_total

    total_hits = ffuf_hits_total + gob_hits_total
    if total_hits:
        _bf_log(f"  {C.G_BRIGHT}[✔]{C.RESET}  {C.c(host):55s}  "
                f"total paths: {C.G_BRIGHT}{C.BOLD}{total_hits}{C.RESET}")
    else:
        _bf_log(f"  {C.GRAY}[−]{C.RESET}  {C.dim(host):55s}  no paths found")

    time.sleep(sleep_sec * 0.2)   # small per-task cooldown
    return result


def step7_bruteforce(domain: str, wkdir: Path, live_out: Path,
                     extra_headers: list, sleep_sec: float, speed: int = 3):
    step_banner(7, "DIRECTORY BRUTEFORCE  (ffuf + gobuster) — PARALLEL ×10")
    bdir = wkdir / "bruteforce"

    if not live_out.exists():
        err("No live subdomains — skipping bruteforce.")
        return

    # ── wordlists ──────────────────────────────────────────────────────────
    small_wl, big_wl = _pick_wordlist()
    if not small_wl and not big_wl:
        warn("No wordlists found. Install SecLists or dirbuster/dirb wordlists.")
        warn("  sudo apt-get install seclists dirbuster dirb")
        warn("Skipping directory bruteforce.")
        return

    wl_msg = (f"small={C.g(os.path.basename(small_wl))} "  if small_wl else f"small={C.r('none')} ") + \
             (f"big={C.y(os.path.basename(big_wl))}"       if big_wl   else f"big={C.r('none')}")
    info(f"Wordlists  →  {wl_msg}")

    # ── tools ──────────────────────────────────────────────────────────────
    ffuf_bin   = go_bin("ffuf")
    gobust_bin = go_bin("gobuster")
    has_ffuf   = (os.path.isfile(ffuf_bin)   and os.access(ffuf_bin,   os.X_OK)) or tool_exists("ffuf")
    has_gobust = (os.path.isfile(gobust_bin) and os.access(gobust_bin, os.X_OK)) or tool_exists("gobuster")

    if not has_ffuf and not has_gobust:
        warn("Neither ffuf nor gobuster found — skipping directory bruteforce.")
        return

    tools_active = " + ".join(filter(None, ["ffuf" if has_ffuf else "", "gobuster" if has_gobust else ""]))
    info(f"Active tools  →  {C.g(tools_active)}")
    info(f"Workers       →  {C.g(str(BRUTEFORCE_WORKERS))} parallel subdomains")
    info(f"Speed level   →  {C.g(str(speed))}  "
         f"(ffuf threads={C.c(str(FFUF_THREADS.get(speed,40)))}  "
         f"delay={C.y(FFUF_DELAY.get(speed,'0')+'s')})")

    # ── read live subs + load status code buckets ─────────────────────────
    subs = scoped_lines(live_out, domain)
    total = len(subs)

    # build a fast lookup: host → status code from the per-code txt files
    subs_dir    = wkdir / "subdomains"
    code_lookup: dict[str, str] = {}
    for code in ["200","201","204","301","302","303","307","401","403","404","500","503"]:
        code_file = subs_dir / f"{code}.txt"
        if code_file.exists():
            for line in code_file.read_text(errors="ignore").splitlines():
                line = line.strip()
                if line:
                    h = urlparse(line).netloc or line
                    code_lookup[h] = code

    hdr_ffuf = " ".join(f'-H "{h}"' for h in (extra_headers or []))
    hdr_gob  = " ".join(f'--headers "{h}"' for h in (extra_headers or []))

    # ── build task list ────────────────────────────────────────────────────
    tasks = []
    skipped_pre = 0
    for idx, sub in enumerate(subs):
        url  = sub if sub.startswith("http") else f"https://{sub}"
        host = urlparse(url).netloc or url
        code = code_lookup.get(host, "200")   # default to 200 if unknown

        tasks.append({
            "url": url, "host": host, "bdir": bdir,
            "small_wl": small_wl, "big_wl": big_wl,
            "header_args_ffuf": hdr_ffuf, "header_args_gob": hdr_gob,
            "has_ffuf": has_ffuf, "has_gobust": has_gobust,
            "speed": speed, "sleep_sec": sleep_sec,
            "status_code": code, "idx": idx, "total": total,
        })

    interesting = [t for t in tasks if t["status_code"] in BRUTEFORCE_INTERESTING]
    boring      = len(tasks) - len(interesting)

    info(f"Subdomains to bruteforce  →  {C.g(str(len(interesting)))} interesting  "
         f"({C.dim(str(boring))} skipped — not in {sorted(BRUTEFORCE_INTERESTING)})")
    print()

    # ── parallel execution ─────────────────────────────────────────────────
    completed_count = 0
    total_paths     = 0
    total_skipped   = 0

    with ThreadPoolExecutor(max_workers=BRUTEFORCE_WORKERS) as pool:
        futures = {pool.submit(_bruteforce_one, t): t for t in tasks}

        for future in as_completed(futures):
            completed_count += 1
            try:
                res = future.result()
                if res.get("skipped"):
                    total_skipped += 1
                else:
                    total_paths += res.get("ffuf_hits", 0) + res.get("gob_hits", 0)
            except Exception as ex:
                with _bf_print_lock:
                    err(f"Worker error: {ex}")

            # global progress bar (thread-safe)
            with _bf_print_lock:
                progress_bar("Bruteforce progress", total, completed_count)

    print()
    ok(f"Parallel bruteforce done  →  {C.g(str(total_paths))} total paths found  "
       f"|  {C.dim(str(total_skipped))} subdomains skipped")
    completed("Directory Bruteforce", total_paths)

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 8  ─  PARAMETER DISCOVERY  (arjun) — PARALLEL + SMART FILTER
# ─────────────────────────────────────────────────────────────────────────────

# Keywords that signal a URL is worth parameter fuzzing
PARAM_INTERESTING_KEYWORDS = [
    "?", "api", "search", "login", "filter", "query", "find",
    "get", "fetch", "load", "view", "show", "list", "read",
    "user", "account", "profile", "auth", "token", "data",
    "report", "export", "download", "upload", "submit", "form",
    "index", "item", "product", "order", "page", "category",
]

# arjun delay flags mapped to speed levels
ARJUN_DELAY = {1: 500, 2: 400, 3: 300, 4: 200, 5: 100}   # milliseconds
ARJUN_CHUNK = {1: 50,  2: 75, 3: 100, 4: 125, 5: 150} # params per chunk

# Workers for parallel arjun scans
ARJUN_WORKERS = 3

# Thread-safe print lock for arjun workers
_arjun_lock = threading.Lock()

def _arjun_log(msg: str):
    with _arjun_lock:
        print(msg)

def _is_interesting_url(url: str) -> bool:
    """Return True if the URL looks worth parameter fuzzing."""
    url_lower = url.lower()
    return any(kw in url_lower for kw in PARAM_INTERESTING_KEYWORDS)

def _collect_endpoint_urls(wkdir: Path, live_out: Path) -> list[str]:
    """
    Build a rich URL list from:
      1. Live subdomains (base URLs)
      2. ffuf/gobuster hits from bruteforce step (discovered paths)
    Then filter to interesting ones only.
    """
    endpoints: set[str] = set()

    # base live URLs
    if live_out.exists():
        for line in live_out.read_text(errors="ignore").splitlines():
            line = line.strip()
            if line:
                endpoints.add(line if line.startswith("http") else f"https://{line}")

    # discovered paths from bruteforce output
    bdir = wkdir / "bruteforce"
    if bdir.exists():
        for jf in bdir.glob("*_ffuf*.json"):
            try:
                data = json.loads(jf.read_text(errors="ignore"))
                for hit in data.get("results", []):
                    path  = hit.get("input", {}).get("FUZZ", "")
                    base  = hit.get("url", "").replace("/FUZZ", "")
                    if path and base:
                        endpoints.add(f"{base.rstrip('/')}/{path.lstrip('/')}")
            except Exception:
                pass
        for tf in bdir.glob("*_gobuster*.txt"):
            base_host = tf.stem.replace("_gobuster_small","").replace("_gobuster_big","").replace("_gobuster","")
            for line in tf.read_text(errors="ignore").splitlines():
                m = re.search(r'(/\S+)', line)
                if m:
                    endpoints.add(f"https://{base_host}{m.group(1)}")

    # filter to interesting only
    interesting = [u for u in sorted(endpoints) if _is_interesting_url(u)]
    return interesting

def _arjun_scan_one(task: dict) -> dict:
    """Worker: run arjun on a single URL."""
    url      = task["url"]
    pdir     = task["pdir"]
    speed    = task["speed"]
    sleep_sec= task["sleep_sec"]
    idx      = task["idx"]
    total    = task["total"]

    host    = urlparse(url).netloc or url
    slug    = re.sub(r'[^\w\-]', '_', url.replace("https://","").replace("http://",""))[:80]
    out_f   = pdir / f"{slug}_params.json"

    delay_ms = ARJUN_DELAY.get(speed, 100)
    chunk    = ARJUN_CHUNK.get(speed, 250)
    delay_flag = f"-d {delay_ms}" if delay_ms > 0 else ""

    _arjun_log(f"  {C.B_BRIGHT}[{idx+1}/{total}]{C.RESET}  {C.c(url[:70])}")

    time.sleep(sleep_sec * 0.3)   # staggered WAF-safe start
    run_cmd(
        f'arjun -u "{url}" --stable --chunk-size {chunk} {delay_flag} '
        f'-o {out_f} -q 2>/dev/null',
        timeout=240
    )

    result = {"url": url, "host": host, "params": [], "out_f": str(out_f)}

    if out_f.exists() and out_f.stat().st_size > 5:
        try:
            data   = json.loads(out_f.read_text(errors="ignore"))
            params = list(data.keys()) if isinstance(data, dict) else []
            result["params"] = params
            if params:
                _arjun_log(
                    f"  {C.G_BRIGHT}[+]{C.RESET}  {C.c(host):45s}  "
                    f"→  {C.G_BRIGHT}{C.BOLD}{len(params)}{C.RESET} params  "
                    f"{C.Y_BRIGHT}{params[:6]}{C.RESET}"
                )
            else:
                _arjun_log(f"  {C.GRAY}[−]{C.RESET}  {C.dim(host):45s}  →  no params")
        except Exception:
            _arjun_log(f"  {C.Y_BRIGHT}[?]{C.RESET}  {C.dim(host):45s}  →  parse error (raw saved)")
    else:
        _arjun_log(f"  {C.GRAY}[−]{C.RESET}  {C.dim(host):45s}  →  no params")

    return result


def step8_parameters(domain: str, wkdir: Path, live_out: Path,
                     extra_headers: list, sleep_sec: float, speed: int = 3):
    step_banner(8, "PARAMETER DISCOVERY  (arjun) — PARALLEL + SMART FILTER")
    pdir = wkdir / "parameters"

    if not tool_exists("arjun"):
        warn("arjun not found — skipping parameter discovery.")
        warn("Install with:  pip3 install arjun --break-system-packages")
        return

    if not live_out.exists():
        err("No live subdomains — skipping parameter discovery.")
        return

    # ── build smart URL list ───────────────────────────────────────────────
    all_endpoints = _collect_endpoint_urls(wkdir, live_out)
    total_raw     = len(all_endpoints) + sum(
        1 for l in live_out.read_text(errors="ignore").splitlines() if l.strip()
    )

    if not all_endpoints:
        warn("No interesting endpoints found to fuzz — skipping parameter discovery.")
        warn(f"Tip: re-run with -s 3+ after bruteforce discovers paths.")
        return

    info(f"Total URLs collected  →  {C.dim(str(total_raw))}")
    info(f"Interesting endpoints →  {C.g(str(len(all_endpoints)))}  "
         f"{C.dim('(filtered by: ' + ', '.join(PARAM_INTERESTING_KEYWORDS[:8]) + ' …)')}")
    info(f"Workers               →  {C.g(str(ARJUN_WORKERS))}")
    info(f"Speed level           →  {C.g(str(speed))}  "
         f"(chunk={C.c(str(ARJUN_CHUNK.get(speed,250)))}  "
         f"delay={C.y(str(ARJUN_DELAY.get(speed,100))+'ms')})")
    print()

    # ── build task list ────────────────────────────────────────────────────
    tasks = [
        {
            "url": url, "pdir": pdir, "speed": speed,
            "sleep_sec": sleep_sec, "idx": i, "total": len(all_endpoints),
        }
        for i, url in enumerate(all_endpoints)
    ]

    # ── parallel execution ─────────────────────────────────────────────────
    all_results   = []
    done_count    = 0
    total_found   = 0

    with ThreadPoolExecutor(max_workers=ARJUN_WORKERS) as pool:
        futures = {pool.submit(_arjun_scan_one, t): t for t in tasks}
        for future in as_completed(futures):
            done_count += 1
            try:
                res = future.result()
                all_results.append(res)
                total_found += len(res.get("params", []))
            except Exception as ex:
                with _arjun_lock:
                    err(f"Worker error: {ex}")
            with _arjun_lock:
                progress_bar("arjun scan progress", len(tasks), done_count)

    print()

    # ── summary md ────────────────────────────────────────────────────────
    md_lines = [f"# Parameter Discovery — {domain}\n\n",
                f"> Speed: {speed}  |  Endpoints scanned: {len(all_endpoints)}  "
                f"|  Total params found: {total_found}\n\n---\n\n"]
    for res in all_results:
        params = res.get("params", [])
        if params:
            md_lines.append(f"## {res['host']}\n\n**URL:** `{res['url']}`\n\n")
            md_lines.append("**Parameters:**\n\n```\n" + "\n".join(params) + "\n```\n\n")
    (pdir / "parameters.md").write_text("".join(md_lines))

    ok(f"Parameter report  →  {C.g('parameters/parameters.md')}")
    completed("Parameter Discovery", total_found)

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 9  ─  JS FILE SECRETS SCANNER
# ─────────────────────────────────────────────────────────────────────────────
JS_PATTERNS = {
    "AWS Access Key":        r'AKIA[0-9A-Z]{16}',
    "AWS Secret Key":        r'(?i)aws.{0,20}secret.{0,20}[\'"][0-9A-Za-z/+=]{40}[\'"]',
    "Generic API Key":       r'(?i)(api[_-]?key|apikey)\s*[:=]\s*[\'"]?[A-Za-z0-9_\-]{16,64}[\'"]?',
    "Generic Secret":        r'(?i)(secret|secret_key|secretkey)\s*[:=]\s*[\'"]?[A-Za-z0-9_\-]{8,64}[\'"]?',
    "Password in code":      r'(?i)(password|passwd|pwd)\s*[:=]\s*[\'"][^\'"\s]{4,}[\'"]',
    "Bearer Token":          r'(?i)bearer\s+[A-Za-z0-9\-_\.]{20,}',
    "Authorization Header":  r'(?i)authorization\s*[:=]\s*[\'"]?[A-Za-z0-9\-_\.]{10,}[\'"]?',
    "Google API Key":        r'AIza[0-9A-Za-z\-_]{35}',
    "Stripe Key":            r'(?:r|s)k_(?:live|test)_[0-9a-zA-Z]{24,}',
    "SendGrid Key":          r'SG\.[A-Za-z0-9\-_]{22}\.[A-Za-z0-9\-_]{43}',
    "Private Key":           r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    "JWT Token":             r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',
    "Generic Flag/CTF":      r'(?i)(flag|ctf)\s*[:={]\s*[\'"]?[A-Za-z0-9_@!\-]{6,}[\'"]?',
    "Firebase URL":          r'https://[a-z0-9\-]+\.firebaseio\.com',
    "Slack Token":           r'xox[baprs]-[0-9A-Za-z\-]{10,}',
    "GitHub Token":          r'ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{82}',
    "Twilio Key":            r'SK[0-9a-fA-F]{32}',
    "Hardcoded URL":         r'https?://(?:localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+)[:/\w]*',
    "Internal IP":           r'\b(?:10|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d+\.\d+\b',
    "SSH Private Key":       r'-----BEGIN OPENSSH PRIVATE KEY-----',
}

def _extract_js_urls(html_content: str, base_url: str) -> list:
    """Extract JS file URLs from HTML source."""
    pattern = r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']'
    found_urls = re.findall(pattern, html_content, re.IGNORECASE)
    result = []
    parsed = urlparse(base_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    for u in found_urls:
        if u.startswith("http"):
            result.append(u)
        elif u.startswith("//"):
            result.append(f"{parsed.scheme}:{u}")
        elif u.startswith("/"):
            result.append(f"{base}{u}")
        else:
            result.append(f"{base}/{u}")
    return list(set(result))

def _scan_js_content(content: str) -> dict:
    """Scan JS content for secrets, return dict of {pattern_name: [matches]}."""
    findings = {}
    for label, pattern in JS_PATTERNS.items():
        matches = re.findall(pattern, content)
        if matches:
            findings[label] = list(set(str(m) for m in matches))[:5]
    return findings

def step9_js_secrets(domain: str, wkdir: Path, live_out: Path,
                     extra_headers: list, sleep_sec: float):
    step_banner(9, "JS FILE SECRETS SCANNER  (keys / passwords / tokens / flags)")
    jsdir   = wkdir / "js_secrets"
    js_md   = jsdir / "js_secrets.md"

    if not live_out.exists():
        err("No live subdomains — skipping JS scan.")
        return

    subs  = scoped_lines(live_out, domain)
    total = len(subs)
    header_args = " ".join(f"-H {shlex.quote(h)}" for h in (extra_headers or []))
    md_lines = [f"# JS File Secrets Scan — {domain}\n\n"]
    total_secrets = 0
    total_js_files = 0

    for idx, sub in enumerate(subs):
        url  = sub if sub.startswith("http") else f"https://{sub}"
        host = urlparse(url).netloc or url
        info(f"  [{idx+1}/{total}]  Scanning JS files on {C.c(host)} …")
        md_lines.append(f"\n## {host}\n\n")

        # fetch main page to extract JS URLs
        rc, html, _ = run_cmd(
            f'curl -s --max-time 15 {header_args} "{url}"',
            timeout=25
        )
        js_urls = [u for u in _extract_js_urls(html, url) if in_scope_url(u, domain)]

        # also check /js/ path
        common_paths = ["main.js","app.js","bundle.js","vendor.js","chunk.js",
                        "webpack.js","index.js","config.js","env.js"]
        for cp in common_paths:
            js_urls.append(f"{url.rstrip('/')}/{cp}")

        js_urls = list(dict.fromkeys(u for u in js_urls if in_scope_url(u, domain)))[:50]  # cap at 50 in-scope JS files per host
        total_js_files += len(js_urls)
        host_secrets = 0

        for js_url in js_urls:
            rc2, js_content, _ = run_cmd(
                f'curl -s --max-time 15 {header_args} "{js_url}"',
                timeout=25
            )
            if not js_content or len(js_content) < 50:
                continue
            if "<html" in js_content.lower()[:200]:
                continue  # not actually JS

            findings = _scan_js_content(js_content)
            if findings:
                js_filename = js_url.split("/")[-1][:40]
                for label, matches in findings.items():
                    for match in matches:
                        # mask sensitive data partially
                        masked = match[:6] + "*" * min(len(match)-6, 12) + match[-3:] if len(match) > 12 else match
                        found(f"  {C.R_BRIGHT}[SECRET]{C.RESET}  {C.y(label):30s}  {C.c(js_filename):30s}  {C.r(masked)}")
                        md_lines.append(f"- **{label}**: `{masked}` ← `{js_url}`\n")
                        host_secrets += 1
                        total_secrets += 1
            time.sleep(sleep_sec * 0.1)

        if host_secrets == 0:
            miss(f"{C.dim(host):55s}  →  No secrets found in JS files")
            md_lines.append("_No secrets detected in JS files._\n")
        else:
            found(f"{C.c(host):55s}  →  {C.r(str(host_secrets))} potential secrets found!")

        progress_bar("JS secrets scan", total, idx + 1)

    md_lines.append(f"\n---\n## Summary\n\n"
                    f"- JS files analyzed : {total_js_files}\n"
                    f"- Total secrets found: **{total_secrets}**\n")
    js_md.write_text("".join(md_lines))
    ok(f"JS secrets report  →  {C.g('js_secrets/js_secrets.md')}")
    completed("JS File Secrets Scan", total_secrets)

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 10  ─  GENERATE  all_in_one.md
# ─────────────────────────────────────────────────────────────────────────────
def step10_report(domain: str, wkdir: Path, live_out: Path):
    step_banner(10, "GENERATING  all_in_one.md  FINAL REPORT")
    report_file = wkdir / "all_in_one.md"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    live_count = sum(1 for l in live_out.read_text(errors="ignore").splitlines() if l.strip()) if live_out.exists() else 0

    lines = [
        f"# 🔐 AutoScan Report — {domain}\n\n",
        f"> Generated by **AutoScan** | Author: Anas Magane | {now}\n\n",
        "---\n\n",
        "## 📋 Executive Summary\n\n",
        f"| Field | Value |\n|---|---|\n",
        f"| Target Domain | `{domain}` |\n",
        f"| Scan Date | {now} |\n",
        f"| Live Subdomains | {live_count} |\n",
        f"| Workspace | `{wkdir}` |\n",
        "\n---\n\n",
        "## 📁 Report Sections\n\n",
        "| Section | File |\n|---|---|\n",
        "| Subdomains | `subdomains/` |\n",
        "| robots.txt | `robots/robots.md` |\n",
        "| Technologies | `technologies/technology.md` |\n",
        "| Nuclei CVEs | `nuclei/nuclei-cves.txt` |\n",
        "| HTTP Methods | `http_methods/http_methods.md` |\n",
        "| Cookies | `cookies/cookies.md` |\n",
        "| Bruteforce | `bruteforce/` |\n",
        "| Parameters | `parameters/` |\n",
        "| JS Secrets | `js_secrets/js_secrets.md` |\n",
        "\n---\n\n",
    ]

    # embed each section's md file content
    sections = [
        ("🌐 Subdomains Enumeration",    wkdir / "subdomains" / "all_subs.txt"),
        ("🤖 robots.txt",                 wkdir / "robots"     / "robots.md"),
        ("🛠 Technologies",               wkdir / "technologies"/ "technology.md"),
        ("💥 Nuclei CVEs",                wkdir / "nuclei"     / "nuclei-cves.txt"),
        ("🔀 HTTP Methods",               wkdir / "http_methods"/ "http_methods.md"),
        ("🍪 Cookies & Storage",          wkdir / "cookies"    / "cookies.md"),
        ("🔑 JS File Secrets",            wkdir / "js_secrets" / "js_secrets.md"),
    ]

    for title, path in sections:
        lines.append(f"\n---\n\n## {title}\n\n")
        if path.exists():
            content = path.read_text(errors="ignore")
            if path.suffix == ".txt":
                lines.append(f"```\n{content[:5000]}\n```\n")
            else:
                lines.append(content[:8000])
        else:
            lines.append("_No data collected._\n")

    lines.append("\n---\n\n## ⚠️ Manual Follow-Up Checklist\n\n")
    checklist = [
        "Use **Wappalyzer** to identify tech versions manually",
        "Review all 403/401 subdomains for bypass opportunities",
        "Check robots.txt disallow paths manually in browser",
        "Investigate all found JS secrets — rotate/revoke immediately",
        "Test TRACE-enabled hosts for XST attacks",
        "Review ffuf/gobuster results for sensitive paths",
        "Fuzz discovered parameters for SQLi, XSS, SSRF, IDOR",
        "Check Nuclei CVE findings for exploitability",
        "Review cookies for missing HttpOnly / Secure / SameSite flags",
    ]
    for item in checklist:
        lines.append(f"- [ ] {item}\n")

    lines.append("\n---\n\n> _AutoScan generates potential findings only; manually validate each result. Scan only assets you are authorized to test._\n")
    report_file.write_text("".join(lines))
    ok(f"Final report  →  {C.g(str(report_file))}")
    completed("Final Report Generation")

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print(BANNER)

    parser  = build_parser()
    args    = parser.parse_args()
    cfg     = load_config()

    # ── --set-api-key shortcut ──────────────────────────────────────────────
    if args.set_api_key:
        cfg["securitytrails"]["api_key"] = args.set_api_key
        save_config(cfg)
        ok(f"SecurityTrails API key saved to {C.g(str(CONFIG_FILE))}")
        sys.exit(0)

    # ── require -u ─────────────────────────────────────────────────────────
    if not args.url:
        parser.print_help()
        print(f"\n  {C.R_BRIGHT}[✘]{C.RESET}  {C.r('Please specify a target with -u <domain>')}\n")
        sys.exit(1)

    parsed_target = urlparse(args.url if "://" in args.url else "https://" + args.url)
    domain = (parsed_target.hostname or "").lower().rstrip(".")
    labels = domain.split(".")
    valid_domain = (len(domain) <= 253 and len(labels) >= 2 and all(
        1 <= len(label) <= 63 and re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", label)
        for label in labels
    ))
    if not valid_domain:
        err(f"Invalid target domain: {C.r(domain or args.url)}")
        sys.exit(1)

    # Custom headers are passed through command-line tools. Reject shell syntax
    # and quote each header separately before building commands.
    for header in (args.headers or []):
        if not re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+\s*:\s*[^\r\n]*", header):
            err("Invalid header format. Use 'Name: value' on one line.")
            sys.exit(1)
        if any(ch in header for ch in ['"', "'", "\\", "`", "$", "|", ";", "&", "<", ">"]):
            err("Header contains shell-sensitive characters; remove them and retry.")
            sys.exit(1)

    # ── resolve API key ────────────────────────────────────────────────────
    st_api_key = (args.api_key or os.environ.get("SECURITYTRAILS_API_KEY") or
                  cfg.get("securitytrails", "api_key", fallback="")).strip()
    if not st_api_key:
        warn("SecurityTrails API key not configured; that source will be skipped. "
             "Set SECURITYTRAILS_API_KEY or use --set-api-key YOUR_KEY.")

    # ── speed ──────────────────────────────────────────────────────────────
    speed = args.speed or int(cfg.get("general","speed", fallback="3"))
    speed = max(1, min(5, speed))
    sleep_sec = SPEED_SLEEP[speed]
    info(f"Scan speed: {C.g(str(speed))}/5  →  sleep between requests: {C.c(str(sleep_sec)+'s')}")

    # ── headers ─────────────────────────────────────────────────────────────
    extra_headers = args.headers or []
    if extra_headers:
        info(f"Custom headers: {C.y(str(extra_headers))}")

    # ── proxy ──────────────────────────────────────────────────────────────
    if args.proxy:
        os.environ["http_proxy"]  = args.proxy
        os.environ["https_proxy"] = args.proxy
        info(f"Proxy: {C.y(args.proxy)}")

    use_headless = bool(args.headless_storage)
    info(f"Target: {C.G_BRIGHT}{C.BOLD}{domain}{C.RESET}")
    info(f"Date  : {C.c(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}")

    # ── CTRL+C handler ─────────────────────────────────────────────────────
    def _sig(sig, frame):
        spinner_stop()
        print(f"\n\n  {C.R_BRIGHT}[!]  Scan interrupted by user.{C.RESET}\n")
        sys.exit(0)
    signal.signal(signal.SIGINT, _sig)

    # ═══════════════════  PIPELINE  ════════════════════════════════════════
    wkdir    = step0_setup(domain)
    live_out = step1_subdomains(domain, wkdir, st_api_key, extra_headers, sleep_sec)
    step2_robots(domain, wkdir, live_out, extra_headers, sleep_sec)
    step3_technologies(domain, wkdir, live_out, extra_headers, sleep_sec)
    step4_nuclei(domain, wkdir, live_out, sleep_sec)
    step5_http_methods(domain, wkdir, live_out, extra_headers, sleep_sec)
    step6_cookies(domain, wkdir, live_out, extra_headers, sleep_sec, use_headless)
    step7_bruteforce(domain, wkdir, live_out, extra_headers, sleep_sec, speed)
    step8_parameters(domain, wkdir, live_out, extra_headers, sleep_sec, speed)
    step9_js_secrets(domain, wkdir, live_out, extra_headers, sleep_sec)
    step10_report(domain, wkdir, live_out)

    # ── FINAL SUMMARY ──────────────────────────────────────────────────────
    print(f"\n{C.G_DIM}{'═'*90}{C.RESET}")
    print(f"  {C.G_BRIGHT}{C.BOLD}  🏁  AUTOSCAN COMPLETE  🏁{C.RESET}")
    print(f"  {C.W_BRIGHT}  Workspace  →  {C.G_BRIGHT}{C.BOLD}{wkdir}{C.RESET}")
    print(f"  {C.C_BRIGHT}  Full report →  {C.G_BRIGHT}{wkdir}/all_in_one.md{C.RESET}")
    print(f"{C.G_DIM}{'═'*90}{C.RESET}\n")
    print(f"  {C.M_BRIGHT}  Happy Hacking 🎯  —  Anas Magane{C.RESET}\n")

if __name__ == "__main__":
    main()