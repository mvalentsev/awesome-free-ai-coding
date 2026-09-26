"""The map of this repository: every file it tracks, what the file is, what it
is made from and what writes it.

The files here depend on each other the way a build does. The registry feeds
every generated page and config, the history feeds the feed and the provider
pages, the watchlist feeds the count on both front pages, and the scheduled run
commits a list of them. Until 2026-09-24 that graph lived in people's heads and
in CONTRIBUTING's prose, and every edge nobody wrote down was a slip waiting to
happen: a watchlist commit that left the pages' count one behind (b1c7f4b), a fix
that reached three of the five pages naming the LiteLLM groups (2717f60), a
README edit the site never saw.

So it is written down, once, here. `freetier-check` refuses a tracked file the
map does not name, a line that names no file and a page the site serves or
leaves out against the map; `freetier-render` prints the map into
CONTRIBUTING.md; the scheduled run commits the files the map says it writes
(`freetier-map paths run`); and the hand-edit guard asks the map before anyone
edits a file only a command may write (`freetier-map may-edit`).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from fnmatch import fnmatchcase
from pathlib import Path

import yaml

__all__ = ["Kind", "Node", "MAP", "node_for", "tracked_files", "check_layout", "run_paths",
           "markdown_table", "main"]


class Kind(str, Enum):
    DATA = "data"            # curated by hand, validated by freetier-check
    LOG = "log"              # append-only, written by a command and never by hand
    GENERATED = "generated"  # written by freetier-render from the data; never by hand
    PAGE = "page"            # written by hand and published as it is
    DOC = "doc"              # written by hand for the people who work on the list
    CODE = "code"            # the package, its templates and its tests
    CONFIG = "config"        # the workflows, the site, the project and its hooks


@dataclass(frozen=True)
class Node:
    """One line of the map: a file, or a glob of files whose `*` stops at a slash."""
    path: str
    kind: Kind
    about: str
    made_from: tuple[str, ...] = ()
    # The commands that write it. A curated file is written by hand as well,
    # which the kind already says.
    written_by: tuple[str, ...] = ()
    # Served by the Pages site. Jekyll serves every file `exclude` in
    # _config.yml does not name, apart from dot and underscore paths.
    published: bool = False
    # A file that exists only once a command first writes it.
    optional: bool = False


# The commands the scheduled run executes before its verification commit, and
# so the writers whose files that commit has to carry.
RUN_WRITERS = ("freetier-probe", "freetier-tiers", "freetier-render")

_PAGES = ("registry.yaml", "watchlist.yaml", "history.jsonl")

MAP: tuple[Node, ...] = (
    # ---- curated data
    Node("registry.yaml", Kind.DATA,
         "every row the list has published, live or archived — the single source of truth",
         written_by=("freetier-probe", "freetier-tiers", "freetier-scout"), published=True),
    Node("watchlist.yaml", Kind.DATA,
         "services checked and not listed: the date, the reason, what would reopen them",
         published=True),
    Node("blocklist.yaml", Kind.DATA, "domains rejected for cause", published=True),
    Node("sources.yaml", Kind.DATA, "lists read once and put down", published=True),
    Node("dismissed.yaml", Kind.DATA, "model-generation bumps a reviewer declined",
         published=True),
    # ---- logs
    Node("history.jsonl", Kind.LOG,
         "every change to what the list publishes, one event a line, append-only",
         made_from=("registry.yaml",), written_by=("freetier-render",), published=True),
    Node("announced.jsonl", Kind.LOG, "the posts the announcer has sent, append-only",
         made_from=("history.jsonl",), written_by=("freetier-announce",), published=True,
         optional=True),
    # ---- generated
    Node("README.md", Kind.GENERATED, "the landing page GitHub shows under the file list",
         made_from=("templates/README.md.j2", *_PAGES), written_by=("freetier-render",)),
    Node("index.html", Kind.GENERATED, "the Pages site's front page",
         made_from=("templates/index.html.j2", *_PAGES), written_by=("freetier-render",),
         published=True),
    Node("configs/README.md", Kind.GENERATED, "the connection table, beside the configs",
         made_from=("templates/configs-README.md.j2", *_PAGES),
         written_by=("freetier-render",)),
    Node("configs/opencode.json", Kind.GENERATED, "the opencode config",
         made_from=("registry.yaml",), written_by=("freetier-render",), published=True),
    Node("configs/litellm.yaml", Kind.GENERATED, "the LiteLLM proxy config and its groups",
         made_from=("registry.yaml",), written_by=("freetier-render",), published=True),
    Node("configs/free-llm.env.example", Kind.GENERATED, "one export per key",
         made_from=("registry.yaml",), written_by=("freetier-render",), published=True),
    Node("configs/claude-code.sh", Kind.GENERATED,
         "one Claude Code shell function per Anthropic-format lane",
         made_from=("registry.yaml",), written_by=("freetier-render",), published=True),
    Node("index.json", Kind.GENERATED, "every row and the watchlist, for machines",
         made_from=("registry.yaml", "watchlist.yaml"), written_by=("freetier-render",),
         published=True),
    Node("feed.xml", Kind.GENERATED, "the Atom feed of the history",
         made_from=("history.jsonl", "registry.yaml"), written_by=("freetier-render",),
         published=True),
    Node("llms.txt", Kind.GENERATED, "the whole list as one text file",
         made_from=("registry.yaml",), written_by=("freetier-render",), published=True),
    Node("providers/*.md", Kind.GENERATED,
         "a page per row, the provider index and the page of services checked",
         made_from=("registry.yaml", "history.jsonl", "watchlist.yaml", "blocklist.yaml"),
         written_by=("freetier-render",), published=True),
    Node("models/*.md", Kind.GENERATED,
         "a page per widely served or strong free model, and the index of every free model",
         made_from=("registry.yaml", "history.jsonl"), written_by=("freetier-render",),
         published=True),
    # ---- hand-written pages
    Node("browse.html", Kind.PAGE, "the filterable table, reading index.json in the browser",
         made_from=("index.json",), published=True),
    Node("assets/*.svg", Kind.PAGE, "the banners and the social preview's source",
         published=True),
    Node("assets/*.png", Kind.PAGE, "the social preview", published=True),
    Node("eb68c254f1e03877b906ccc800002691.txt", Kind.PAGE,
         "the IndexNow key, named after itself (indexnow.INDEXNOW_KEY)", published=True),
    # ---- docs
    Node("CONTRIBUTING.md", Kind.DOC,
         "how the list works and how to change it; its map section is this table",
         made_from=("src/freetier_radar/layout.py",), written_by=("freetier-render",),
         published=True),
    Node("LICENSE", Kind.DOC, "MIT", published=True),
    Node("assets/README.md", Kind.DOC, "what each asset is for"),
    # ---- code
    Node("src/freetier_radar/*.py", Kind.CODE, "the probe, the scout, the render and the checks"),
    Node("templates/*.j2", Kind.CODE, "the page templates freetier-render fills"),
    Node("tests/*.py", Kind.CODE, "the test suite"),
    # ---- config
    Node("pyproject.toml", Kind.CONFIG, "the package and its commands"),
    Node("uv.lock", Kind.CONFIG, "the pinned dependencies"),
    Node("_config.yml", Kind.CONFIG, "the Pages site: its name, its plugins, what it leaves out"),
    Node(".gitignore", Kind.CONFIG, "what git leaves alone"),
    Node(".githooks/*", Kind.CONFIG,
         "the git hooks that run freetier-gate — `git config core.hooksPath .githooks`"),
    Node(".github/workflows/*.yml", Kind.CONFIG, "CI, the scheduled run and read-page"),
    Node(".github/dependabot.yml", Kind.CONFIG, "the pinned actions' watcher"),
    Node(".github/ISSUE_TEMPLATE/*.yml", Kind.CONFIG, "the suggest-a-service form"),
)


def _matches(path: str, pattern: str) -> bool:
    """A glob whose `*` stops at a slash: the same number of parts, each matched."""
    parts, want = path.split("/"), pattern.split("/")
    return len(parts) == len(want) and all(fnmatchcase(p, w) for p, w in zip(parts, want))


def _claims(path: str, nodes: tuple[Node, ...]) -> list[Node]:
    return [n for n in nodes if _matches(path, n.path)]


def node_for(path: str, nodes: tuple[Node, ...] = MAP) -> Node | None:
    found = _claims(path, nodes)
    return found[0] if found else None


# What a snapshot of the index can hold beside the tracked files once a check
# has run in it.
_NOT_TRACKED = {".git", "__pycache__", ".pytest_cache", ".venv"}


def tracked_files(root: Path) -> list[str]:
    """The files git tracks under `root` — or, where `root` is not a work tree
    (the pre-commit gate's snapshot of the index), every file in it."""
    listed = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True)
    inside = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"],
                            capture_output=True, text=True)
    if listed.returncode == 0 and inside.returncode == 0 \
            and Path(inside.stdout.strip()).resolve() == root.resolve():
        return sorted(p for p in listed.stdout.decode("utf-8").split("\0") if p)
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*")
                  if p.is_file() and not _NOT_TRACKED & set(p.relative_to(root).parts))


def _site_exclude(root: Path) -> list[str]:
    config = yaml.safe_load((root / "_config.yml").read_text(encoding="utf-8")) or {}
    return [str(e) for e in config.get("exclude") or []]


def _served(path: str, exclude: list[str]) -> bool:
    if any(part.startswith((".", "_")) for part in path.split("/")):
        return False
    return not any(path == e.rstrip("/") or path.startswith(e.rstrip("/") + "/")
                   for e in exclude)


def check_layout(root: Path | None = None, files: list[str] | None = None,
                 nodes: tuple[Node, ...] = MAP, exclude: list[str] | None = None) -> list[str]:
    """Every way the tracked files and the map can disagree, as readable lines."""
    files = tracked_files(root) if files is None else files
    exclude = _site_exclude(root) if exclude is None else exclude
    problems = []
    for f in files:
        found = _claims(f, nodes)
        if not found:
            problems.append(f"{f} is on no line of the map (layout.MAP) — say what it is, "
                            "what it is made from and what writes it")
            continue
        if len(found) > 1:
            problems.append(f"{f} is on two lines of the map, "
                            + " and ".join(n.path for n in found))
            continue
        served, node = _served(f, exclude), found[0]
        if served and not node.published:
            problems.append(f"{f} is served by the Pages site and the map says it is not "
                            "published — add it to exclude in _config.yml, or mark it published")
        elif node.published and not served:
            problems.append(f"{f} is left out of the Pages site by _config.yml and the map says "
                            "it is published")
    for node in nodes:
        if not node.optional and not any(_matches(f, node.path) for f in files):
            problems.append(f"{node.path} is on the map and names no tracked file — the file is "
                            "gone, or the line names it wrong")
    return problems


def run_paths(nodes: tuple[Node, ...] = MAP) -> list[str]:
    """What the scheduled run's verification commit adds: every file a command
    of the run writes, a globbed line as its directory, so a page the render
    removes is committed as removed."""
    paths = []
    for node in nodes:
        if set(node.written_by) & set(RUN_WRITERS):
            path = node.path.rsplit("/", 1)[0] if "*" in node.path else node.path
            if path not in paths:
                paths.append(path)
    return paths


def _code(items: tuple[str, ...]) -> str:
    return ", ".join(f"`{i}`" for i in items) or "—"


def markdown_table(nodes: tuple[Node, ...] = MAP) -> str:
    """The map as the table CONTRIBUTING.md prints."""
    rows = ["| File | What it is | Made from | Written by |", "|---|---|---|---|"]
    for n in nodes:
        by = n.written_by if n.kind in (Kind.LOG, Kind.GENERATED) else ("hand", *n.written_by)
        what = f"**{n.kind.value}** — {n.about}" + ("" if n.published else " · not on the site")
        rows.append(f"| `{n.path}` | {what} | {_code(n.made_from)} | {_code(by)} |")
    return "\n".join(rows)


def _explain(path: str, node: Node) -> str:
    if node.kind is Kind.GENERATED:
        return (f"{path} is generated by freetier-render from {', '.join(node.made_from)} — "
                "edit those and run `TZ=UTC uv run freetier-render`, never the file itself")
    return (f"{path} is append-only and written by {' and '.join(node.written_by)} alone — "
            "a hand edit would rewrite what the list has published")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="The map of the repository: what every tracked file is and what writes it.")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("table", help="print the map as a Markdown table (the default)")
    paths = sub.add_parser("paths", help="print the paths a writer's files live at")
    paths.add_argument("who", choices=["run"], help="run: what the scheduled run commits")
    may = sub.add_parser("may-edit", help="exit 1, saying why, for a file no hand may edit")
    may.add_argument("files", nargs="+")
    args = parser.parse_args(argv)
    if args.command == "paths":
        print("\n".join(run_paths()))
    elif args.command == "may-edit":
        refused = [(f, node_for(f)) for f in args.files]
        refused = [(f, n) for f, n in refused if n and n.kind in (Kind.GENERATED, Kind.LOG)]
        for f, node in refused:
            print(_explain(f, node))
        if refused:
            raise SystemExit(1)
    else:
        print(markdown_table())


if __name__ == "__main__":
    main(sys.argv[1:])
