"""
Weather Note Admin
ローカルで起動するブログ管理画面。
起動: make admin  (または FLASK_APP=admin/app.py python -m flask run --port 5001)
"""

import io
import os
import pathlib
import subprocess
import time
import datetime

from flask import Flask, flash, jsonify, redirect, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename
import ruamel.yaml
from slugify import slugify

# ---------------------------------------------------------------------------
# 設定
# ---------------------------------------------------------------------------
ROOT = pathlib.Path(__file__).parent.parent.resolve()   # プロジェクトルート
POSTS_DIR = ROOT / "content" / "posts"
IMAGES_DIR = ROOT / "static" / "images"
SITE_URL = "https://weathernote.github.io/weather-note/"
PREVIEW_URL = "http://localhost:1313/weather-note/"
SITE_BASE_PATH = "/weather-note"   # GitHub Pages のサブパス

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "svg"}

app = Flask(__name__)
app.secret_key = os.urandom(24)   # flash メッセージ用

# ---------------------------------------------------------------------------
# ヘルパー: YAML
# ---------------------------------------------------------------------------
def _yaml():
    y = ruamel.yaml.YAML()
    y.preserve_quotes = True
    y.default_flow_style = False
    y.width = 4096
    return y


def _parse_post(filepath: pathlib.Path):
    """ファイルを読んで (frontmatter_dict, body_str) を返す。"""
    text = filepath.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    _, fm_raw, body = parts
    fm = _yaml().load(fm_raw) or {}
    return fm, body.lstrip("\n")


def _dump_frontmatter(fm) -> str:
    y = _yaml()
    buf = io.StringIO()
    y.dump(fm, buf)
    return buf.getvalue()


def _write_post(slug: str, fm, body: str):
    """フロントマターと本文をアトミックにファイルへ書き込む。"""
    content = f"---\n{_dump_frontmatter(fm)}---\n\n{body}"
    target = POSTS_DIR / f"{slug}.md"
    tmp = target.with_suffix(".md.tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(target)


# ---------------------------------------------------------------------------
# ヘルパー: 記事一覧・検索
# ---------------------------------------------------------------------------
def _load_meta(filepath: pathlib.Path) -> dict:
    """フロントマターのみ読んでメタ情報 dict を返す（本文は不要）。"""
    fm, _ = _parse_post(filepath)
    slug = filepath.stem
    return {
        "slug": slug,
        "title": fm.get("title") or slug,
        "date": fm.get("date") or "",
        "categories": fm.get("categories") or [],
        "tags": fm.get("tags") or [],
        "draft": bool(fm.get("draft", False)),
    }


def list_posts() -> list[dict]:
    posts = [_load_meta(p) for p in POSTS_DIR.glob("*.md")]
    posts.sort(key=lambda p: str(p["date"]), reverse=True)
    return posts


def read_post(slug: str):
    path = POSTS_DIR / f"{slug}.md"
    if not path.exists():
        return None, None
    return _parse_post(path)


def slug_exists(slug: str) -> bool:
    return (POSTS_DIR / f"{slug}.md").exists()


def all_categories() -> list[str]:
    cats: set[str] = set()
    for p in POSTS_DIR.glob("*.md"):
        fm, _ = _parse_post(p)
        for c in (fm.get("categories") or []):
            cats.add(str(c))
    return sorted(cats)


def all_tags() -> list[str]:
    tags: set[str] = set()
    for p in POSTS_DIR.glob("*.md"):
        fm, _ = _parse_post(p)
        for t in (fm.get("tags") or []):
            tags.add(str(t))
    return sorted(tags)


def title_to_slug(title: str) -> str:
    today = datetime.date.today().strftime("%Y%m%d")
    ascii_part = slugify(title, separator="-")
    if not ascii_part:
        ascii_part = f"post-{int(time.time())}"
    return f"{today}-{ascii_part}"


# ---------------------------------------------------------------------------
# ヘルパー: git
# ---------------------------------------------------------------------------
def run_git(*args) -> tuple[int, str]:
    r = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    return r.returncode, (r.stdout + r.stderr).strip()


# ---------------------------------------------------------------------------
# ルート
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return redirect(url_for("posts_list"))


@app.route("/posts")
def posts_list():
    posts = list_posts()
    return render_template("posts_list.html", posts=posts)


@app.route("/posts/new", methods=["GET", "POST"])
def post_new():
    if request.method == "POST":
        return _save_post(slug=None)

    # GET: 空フォームを表示
    today = datetime.date.today().isoformat()
    suggested_slug = title_to_slug(request.args.get("title", ""))
    fm = {
        "title": request.args.get("title", ""),
        "date": today,
        "categories": [],
        "tags": [],
        "coverImage": "",
        "draft": True,
    }
    return render_template(
        "post_edit.html",
        slug=None,
        fm=fm,
        body="",
        suggested_slug=suggested_slug,
        categories=all_categories(),
        tags=all_tags(),
    )


@app.route("/posts/<slug>/edit", methods=["GET", "POST"])
def post_edit(slug):
    if request.method == "POST":
        return _save_post(slug=slug)

    fm, body = read_post(slug)
    if fm is None:
        flash(f"記事が見つかりません: {slug}", "error")
        return redirect(url_for("posts_list"))

    return render_template(
        "post_edit.html",
        slug=slug,
        fm=fm,
        body=body,
        suggested_slug=slug,
        categories=all_categories(),
        tags=all_tags(),
    )


def _save_post(slug):
    """POST データから記事を保存する共通処理。"""
    form = request.form

    new_slug = form.get("slug", "").strip()
    if not new_slug:
        flash("スラグを入力してください。", "error")
        return redirect(request.referrer or url_for("posts_list"))

    # 新規 & スラグ重複チェック
    if slug is None and slug_exists(new_slug):
        flash(f"スラグ「{new_slug}」は既に存在します。別のスラグを指定してください。", "error")
        return redirect(url_for("post_new"))

    # カテゴリ・タグをカンマ区切りから list へ
    categories = [c.strip() for c in form.get("categories", "").split(",") if c.strip()]
    tags = [t.strip() for t in form.get("tags", "").split(",") if t.strip()]

    # フロントマター組み立て
    y = _yaml()
    fm = y.load(f"title: ''\ndate: ''\ncategories: []\ntags: []\ncoverImage: ''\ndraft: false\n")
    fm["title"] = form.get("title", "").strip()
    fm["date"] = form.get("date", datetime.date.today().isoformat())
    fm["categories"] = categories
    fm["tags"] = tags
    fm["coverImage"] = form.get("coverImage", "").strip()
    fm["draft"] = "draft" in form

    body = form.get("body", "")

    _write_post(new_slug, fm, body)
    flash(f"保存しました: {new_slug}", "success")
    return redirect(url_for("post_edit", slug=new_slug))


@app.route("/posts/<slug>/delete", methods=["POST"])
def post_delete(slug):
    path = POSTS_DIR / f"{slug}.md"
    if path.exists():
        path.unlink()
        flash(f"削除しました: {slug}", "success")
    else:
        flash(f"記事が見つかりません: {slug}", "error")
    return redirect(url_for("posts_list"))


@app.route("/publish", methods=["GET", "POST"])
def publish():
    _, status_output = run_git("status", "--short")

    if request.method == "POST":
        msg = request.form.get("message", "").strip()
        if not msg:
            flash("コミットメッセージを入力してください。", "error")
            return redirect(url_for("publish"))

        lines = []
        for cmd_args in [
            ["add", "-A"],
            ["commit", "-m", msg],
            ["push"],
        ]:
            code, out = run_git(*cmd_args)
            lines.append(f"$ git {' '.join(cmd_args)}\n{out}")
            # "nothing to commit" は正常終了とみなす
            if code != 0 and "nothing to commit" not in out and "nothing added" not in out:
                lines.append("[エラーが発生しました。以降のコマンドを中断します]")
                break

        git_output = "\n\n".join(lines)
        return render_template(
            "publish.html",
            status_output=status_output,
            git_output=git_output,
            site_url=SITE_URL,
        )

    return render_template(
        "publish.html",
        status_output=status_output,
        git_output=None,
        site_url=SITE_URL,
    )


@app.route("/api/slug")
def api_slug():
    """タイトルからスラグ候補を返す JSON API（エディターの JS から呼び出す）。"""
    title = request.args.get("title", "")
    return jsonify(slug=title_to_slug(title))


@app.route("/api/images")
def api_images():
    """static/images/ にある画像ファイルの一覧を返す（更新日時の降順）。"""
    images = []
    for f in sorted(IMAGES_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if f.suffix.lower().lstrip(".") in ALLOWED_EXTENSIONS:
            images.append({
                "name": f.name,
                "preview_url": f"/admin-img/{f.name}",
                "markdown_url": f"{SITE_BASE_PATH}/images/{f.name}",
            })
    return jsonify(images=images)


@app.route("/api/upload", methods=["POST"])
def api_upload():
    """画像ファイルを static/images/ にアップロードする。"""
    if "file" not in request.files:
        return jsonify(error="ファイルがありません"), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify(error="ファイルが選択されていません"), 400
    ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify(error=f"対応していない形式です（{ext}）。PNG/JPG/GIF/WebP/SVG のみ"), 400

    filename = secure_filename(f.filename)
    dest = IMAGES_DIR / filename
    if dest.exists():
        stem, suffix = os.path.splitext(filename)
        filename = f"{stem}-{int(time.time())}{suffix}"
        dest = IMAGES_DIR / filename

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    f.save(dest)
    return jsonify(
        name=filename,
        preview_url=f"/admin-img/{filename}",
        markdown_url=f"{SITE_BASE_PATH}/images/{filename}",
    )


@app.route("/admin-img/<filename>")
def admin_img(filename):
    """管理画面内で static/images/ の画像をプレビュー表示する。"""
    return send_from_directory(IMAGES_DIR, filename)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
