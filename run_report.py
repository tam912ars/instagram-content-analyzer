"""
run_report.py ─ 毎日レポート自動生成エントリーポイント

実行方法:
  python run_report.py              # 本日のレポートを生成・送信
  python run_report.py --no-mail   # 生成のみ（メール送信なし）
  python run_report.py --dry-run   # RSSは取得するがAI不使用・メール不送信

GitHub Actions から呼び出される際は引数なしで実行される。
"""
import argparse
import logging
import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── ログ設定 ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("run_report")

# プロジェクトルートを sys.path に追加
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))


# ── 各モジュールのインポート ──────────────────────────────────────────────────
from src.trends.rss_fetcher import fetch_rss_news
from src.trends.news_filter import filter_education_news
from src.trends.mock_comments import get_mock_hot_comments
from src.trends.mock_past_posts import get_mock_past_posts
from src.trends.scorer import get_top3_content_ideas, get_dual_summary, score_news_item
from src.instagram.mock_data import generate_mock_posts, generate_mock_account
from src.analysis.post_analyzer import parse_posts, get_comment_keywords, extract_hashtags
from src.ai.content_generator import ContentGenerator
from src.visualization.html_report import generate_html_report
from src.delivery.gmail_sender import send_report_email, _build_report_url


# ── レポートの保存先 ──────────────────────────────────────────────────────────
REPORTS_DIR = ROOT / "reports"


def _generate_index_html(reports_dir: Path) -> None:
    """reports/ 以下のHTMLファイルから一覧ページを自動生成する"""
    html_files = sorted(
        [f for f in reports_dir.glob("????-??-??.html")],
        reverse=True,  # 新しい順
    )

    items_html = ""
    for f in html_files:
        date_str = f.stem  # "2026-04-13"
        try:
            d = date.fromisoformat(date_str)
            label = d.strftime("%Y年%m月%d日")
        except ValueError:
            label = date_str
        items_html += (
            f'<li><a href="{f.name}" '
            f'style="color:#4f46e5;text-decoration:none;font-size:15px;">'
            f'📋 {label}</a></li>\n'
        )

    if not items_html:
        items_html = '<li style="color:#9ca3af;">レポートはまだありません</li>'

    index_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ダイ先生 コンテンツレポート 一覧</title>
  <style>
    body {{ font-family: 'Hiragino Sans', sans-serif; background: #f9fafb;
            display: flex; justify-content: center; padding: 48px 16px; }}
    .card {{ background: #fff; border-radius: 12px; padding: 32px 40px;
             box-shadow: 0 2px 8px rgba(0,0,0,0.08); max-width: 480px; width: 100%; }}
    h1 {{ margin: 0 0 8px; font-size: 20px; color: #1e1b4b; }}
    p  {{ margin: 0 0 24px; font-size: 13px; color: #6b7280; }}
    ul {{ list-style: none; margin: 0; padding: 0; }}
    li {{ padding: 10px 0; border-bottom: 1px solid #f3f4f6; }}
    li:last-child {{ border-bottom: none; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>📊 ダイ先生 コンテンツレポート</h1>
    <p>毎朝 6:30 自動生成・配信</p>
    <ul>
{items_html}
    </ul>
  </div>
</body>
</html>"""

    (reports_dir / "index.html").write_text(index_html, encoding="utf-8")
    logger.info("index.html 更新完了（%d件）", len(html_files))


def run(
    use_mock_instagram: bool = True,
    skip_ai: bool = False,
    skip_mail: bool = False,
) -> Path:
    """
    メインパイプライン。

    Returns
    -------
    Path : 生成された HTML ファイルのパス
    """
    today = date.today()
    logger.info("=== レポート生成開始: %s ===", today.isoformat())

    # ── Step 1: ニュース取得 ──────────────────────────────────────────────
    logger.info("[Step 1] RSS ニュース取得")
    raw_news = fetch_rss_news(max_per_feed=20)
    news_items = filter_education_news(raw_news, max_items=30)
    logger.info("教育ニュース: %d件", len(news_items))

    # フォールバック：RSSが全滅した場合はモックデータを使用
    if not news_items:
        logger.warning("RSSが取得できませんでした。モックデータを使用します。")
        from src.trends.mock_news import get_mock_news
        news_items = get_mock_news()

    # ── Step 2: Instagram データ取得 ─────────────────────────────────────
    logger.info("[Step 2] Instagram データ取得")
    if use_mock_instagram:
        posts = generate_mock_posts(30)
        account = generate_mock_account()
    else:
        # 実際の Instagram API（将来実装）
        from src.instagram.client import InstagramClient
        client = InstagramClient()
        posts = client.get_posts(limit=30)
        account = client.get_account_info()

    df = parse_posts(posts)
    comment_keywords = get_comment_keywords(posts, top_n=20)
    captions = df["caption"].fillna("").tolist() if not df.empty else []
    hashtags = extract_hashtags(captions)
    past_post_captions = [p.get("caption", "") for p in posts[:20]]

    kpi = {
        "followers": account.get("followers_count", 0),
        "avg_likes": int(df["like_count"].mean()) if not df.empty else 0,
        "avg_comments": int(df["comments_count"].mean()) if not df.empty else 0,
        "post_count": len(posts),
    }

    # ── Step 3: スコアリング & TOP3 選定 ─────────────────────────────────
    logger.info("[Step 3] ニュースのスコアリング")
    scored_news = [
        score_news_item(item, comment_keywords, past_post_captions)
        for item in news_items
    ]
    top3_ideas = get_top3_content_ideas(news_items, comment_keywords, past_post_captions)
    dual_summary = get_dual_summary(comment_keywords, news_items)

    # ── Step 4: AI によるコンテンツ案生成 ────────────────────────────────
    logger.info("[Step 4] AI コンテンツ案生成")
    ai_report: dict = {}
    if skip_ai:
        logger.info("--dry-run のため AI をスキップします")
        ai_report = {
            "date": today.strftime("%Y年%m月%d日"),
            "summary": "（ドライランのためAI生成をスキップしました）",
            "instagram_ideas": [],
            "stafy_topics": [],
            "youtube_live_topics": [],
        }
    else:
        try:
            generator = ContentGenerator()
            ai_report = generator.generate_daily_report(
                top_posts=posts[:5],
                comment_keywords=comment_keywords,
                questions=[],
                hashtags=hashtags,
                today=today,
            )
            if "error" in ai_report:
                logger.warning("AI 生成エラー: %s", ai_report.get("error"))
        except Exception as e:
            logger.error("AI 生成失敗: %s", e)
            ai_report = {
                "date": today.strftime("%Y年%m月%d日"),
                "summary": "AI生成に失敗しました。ニュースデータをご確認ください。",
                "instagram_ideas": [],
                "stafy_topics": [],
                "youtube_live_topics": [],
            }

    # ── Step 5: HTML レポート生成 ─────────────────────────────────────────
    logger.info("[Step 5] HTML レポート生成")
    hot_comments = get_mock_hot_comments()
    past_posts = get_mock_past_posts()

    html = generate_html_report(
        report=ai_report,
        account_name=account.get("name", "ダイ先生"),
        kpi=kpi,
        news_items=scored_news,
        top3_ideas=top3_ideas,
        dual_summary=dual_summary,
        hot_comments=hot_comments,
        past_posts=past_posts,
    )

    # ── Step 6: ファイル保存 ──────────────────────────────────────────────
    logger.info("[Step 6] ファイル保存")
    REPORTS_DIR.mkdir(exist_ok=True)
    output_path = REPORTS_DIR / f"{today.isoformat()}.html"
    output_path.write_text(html, encoding="utf-8")
    logger.info("レポート保存: %s", output_path)

    # 一覧ページを更新
    _generate_index_html(REPORTS_DIR)

    # ── Step 7: メール送信 ────────────────────────────────────────────────
    if skip_mail:
        logger.info("[Step 7] メール送信スキップ（--no-mail）")
    else:
        logger.info("[Step 7] メール送信")
        summary_text = ai_report.get("summary", "本日のレポートをご確認ください。")
        top3_titles = [idea.get("title", "") for idea in top3_ideas[:3]]
        report_url = _build_report_url(today)

        success = send_report_email(
            report_date=today,
            summary=summary_text,
            top3_titles=top3_titles,
            report_url=report_url,
        )
        if not success:
            logger.warning("メール送信に失敗しましたが、レポートの生成は完了しています。")

    logger.info("=== レポート生成完了: %s ===", output_path)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="ダイ先生 毎日コンテンツレポート生成")
    parser.add_argument("--no-mail", action="store_true", help="メール送信をスキップ")
    parser.add_argument("--dry-run", action="store_true", help="AI不使用・メール不送信")
    parser.add_argument("--use-real-instagram", action="store_true",
                        help="Instagram Graph API を使用（デフォルトはモック）")
    args = parser.parse_args()

    output = run(
        use_mock_instagram=not args.use_real_instagram,
        skip_ai=args.dry_run,
        skip_mail=args.no_mail or args.dry_run,
    )
    print(f"\n✅ レポート生成完了: {output}")


if __name__ == "__main__":
    main()
