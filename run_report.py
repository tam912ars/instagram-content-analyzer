"""
run_report.py ─ 毎日レポート自動生成エントリーポイント

実行方法:
  python run_report.py              # 本日のレポートを生成・送信
  python run_report.py --no-mail   # 生成のみ（メール送信なし）
  python run_report.py --dry-run   # RSS取得のみ・メール不送信

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
from src.trends.scorer import score_news_item
from src.visualization.html_report import generate_html_report
from src.delivery.gmail_sender import send_report_email, _build_report_url

# ── レポートの保存先 ──────────────────────────────────────────────────────────
REPORTS_DIR = ROOT / "reports"


def _generate_index_html(reports_dir: Path) -> None:
    """reports/ 以下のHTMLファイルから一覧ページを自動生成する"""
    html_files = sorted(
        [f for f in reports_dir.glob("????-??-??.html")],
        reverse=True,
    )

    items_html = ""
    for f in html_files:
        date_str = f.stem
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

    # ── Step 2: スコアリング & Top5 選定 ─────────────────────────────────
    logger.info("[Step 2] ニュースのスコアリング")
    scored_news = [
        score_news_item(item, [], [])
        for item in news_items
    ]
    scored_news.sort(key=lambda x: x.get("composite_score", 0), reverse=True)
    logger.info("上位ニュース: %d件 → Top 5 を使用", len(scored_news))

    # ── Step 3: HTML レポート生成 ─────────────────────────────────────────
    logger.info("[Step 3] HTML レポート生成")
    html = generate_html_report(
        news_items=scored_news,
        account_name="ダイ先生",
        today=today,
    )

    # ── Step 4: ファイル保存 ──────────────────────────────────────────────
    logger.info("[Step 4] ファイル保存")
    REPORTS_DIR.mkdir(exist_ok=True)
    output_path = REPORTS_DIR / f"{today.isoformat()}.html"
    output_path.write_text(html, encoding="utf-8")
    logger.info("レポート保存: %s", output_path)

    _generate_index_html(REPORTS_DIR)

    # ── Step 5: メール送信 ────────────────────────────────────────────────
    if skip_mail:
        logger.info("[Step 5] メール送信スキップ")
    else:
        logger.info("[Step 5] メール送信")
        top5_titles = [item.get("title", "") for item in scored_news[:5]]
        report_url = _build_report_url(today)

        success = send_report_email(
            report_date=today,
            summary=f"本日の教師向けニュース Top5 をピックアップしました。",
            top3_titles=top5_titles[:3],
            report_url=report_url,
        )
        if not success:
            logger.warning("メール送信に失敗しましたが、レポートの生成は完了しています。")

    logger.info("=== レポート生成完了: %s ===", output_path)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="ダイ先生 毎日コンテンツレポート生成")
    parser.add_argument("--no-mail", action="store_true", help="メール送信をスキップ")
    parser.add_argument("--dry-run", action="store_true", help="メール不送信")
    args = parser.parse_args()

    output = run(
        skip_mail=args.no_mail or args.dry_run,
    )
    print(f"\n✅ レポート生成完了: {output}")


if __name__ == "__main__":
    main()
