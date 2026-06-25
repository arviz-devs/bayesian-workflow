#!/usr/bin/env python3
"""Build 1200x630 social cards: book cover (left) + case-study figure (right).

Usage:
    python social_cards/make_cards.py                     # all pages in config
    python social_cards/make_cards.py bioassay            # single page
    python social_cards/make_cards.py --list              # list available figures

Reads social_cards/config.yml for page→figure mapping.
Figures are resolved from _book/<dir>/<page>_files/figure-html/.
"""
import argparse
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
CONFIG_PATH = SCRIPT_DIR / "config.yml"

CARD_W, CARD_H = 1200, 630
COVER_MAX_H = 560
FIG_MAX_W, FIG_MAX_H = 680, 560
COVER_X = 50
FIG_X_FROM_RIGHT = 40
BORDER_COLOR = "#dddddd"
BG_COLOR = "white"


def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def list_figures(cfg):
    book_dir = REPO_DIR / cfg["book_dir"]
    for name, entry in cfg["pages"].items():
        fig_dir = book_dir / entry["dir"] / f"{entry['page']}_files" / "figure-html"
        print(f"\n=== {name}  ({fig_dir.relative_to(REPO_DIR)}) ===")
        if fig_dir.is_dir():
            for p in sorted(fig_dir.glob("*.png")):
                marker = " <-- selected" if p.name == entry["figure"] else ""
                print(f"  {p.name}{marker}")
        else:
            print("  (directory not found)")


def fit_within(img, max_w, max_h):
    img_w, img_h = img.size
    ratio = min(max_w / img_w, max_h / img_h, 1.0)
    if ratio < 1.0:
        new_w = max(1, int(img_w * ratio))
        new_h = max(1, int(img_h * ratio))
        return img.resize((new_w, new_h), Image.LANCZOS)
    return img.copy()


def make_card(cfg, page_name):
    entry = cfg["pages"][page_name]
    book_dir = REPO_DIR / cfg["book_dir"]
    cover_path = REPO_DIR / cfg["cover"]

    fig_path = book_dir / entry["dir"] / f"{entry['page']}_files" / "figure-html" / entry["figure"]
    if not fig_path.is_file():
        print(f"ERROR: figure not found: {fig_path.relative_to(REPO_DIR)}", file=sys.stderr)
        return None

    if not cover_path.is_file():
        print(f"ERROR: cover not found: {cover_path.relative_to(REPO_DIR)}", file=sys.stderr)
        return None

    cover = Image.open(cover_path).convert("RGBA")
    fig_raw = Image.open(fig_path).convert("RGBA")

    cover = fit_within(cover, CARD_W, COVER_MAX_H)
    fig_fitted = fit_within(fig_raw, FIG_MAX_W, FIG_MAX_H)

    fig_panel = Image.new("RGBA", (FIG_MAX_W, FIG_MAX_H), BG_COLOR)
    fx = (FIG_MAX_W - fig_fitted.size[0]) // 2
    fy = (FIG_MAX_H - fig_fitted.size[1]) // 2
    fig_panel.paste(fig_fitted, (fx, fy), fig_fitted)
    draw = ImageDraw.Draw(fig_panel)
    draw.rectangle([0, 0, FIG_MAX_W - 1, FIG_MAX_H - 1], outline=BORDER_COLOR)

    canvas = Image.new("RGBA", (CARD_W, CARD_H), BG_COLOR)

    cover_y = (CARD_H - cover.size[1]) // 2
    canvas.paste(cover, (COVER_X, cover_y), cover)

    fig_x = CARD_W - FIG_MAX_W - FIG_X_FROM_RIGHT
    fig_y = (CARD_H - FIG_MAX_H) // 2
    canvas.paste(fig_panel, (fig_x, fig_y), fig_panel)

    out_dir = REPO_DIR / cfg["output_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{page_name}.png"

    canvas.convert("RGB").save(out_path, "PNG", optimize=True)
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Generate social cards for the site.")
    parser.add_argument("pages", nargs="*", help="page names to generate (default: all)")
    parser.add_argument("--list", action="store_true", help="list available figures per page")
    args = parser.parse_args()

    cfg = load_config()

    if args.list:
        list_figures(cfg)
        return

    page_names = args.pages if args.pages else list(cfg["pages"].keys())

    for name in page_names:
        if name not in cfg["pages"]:
            print(f"WARNING: '{name}' not in config, skipping.", file=sys.stderr)
            continue
        out = make_card(cfg, name)
        if out:
            print(f"Wrote {out.relative_to(REPO_DIR)}  (figure: {cfg['pages'][name]['figure']})")


if __name__ == "__main__":
    main()
