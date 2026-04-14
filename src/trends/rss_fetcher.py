"""
教育ニュース RSS フェッチャー

優先順位：
  高 → 教育新聞・Yahoo!ニュース教育・地方紙ニュース
  低 → コラム・社説・オピニオン（news_filter.py で除外）
"""
import hashlib
import logging
from datetime import date, datetime, timezone, timedelta
from typing import Optional

import feedparser
import requests

logger = logging.getLogger(__name__)

JST = timezone(timedelta(hours=9))

# ── RSS フィード一覧（優先度順） ────────────────────────────────────────────
_GN_BASE = "https://news.google.com/rss/search?hl=ja&gl=JP&ceid=JP:ja&q="

# Google News RSS（キーワード検索）
# → 地方紙・全国紙・Yahoo!ニュースなど多様なソースから教育記事だけを取得できる
RSS_FEEDS: list[dict] = [
    # ① 教員・教師ニュース（最優先）
    {
        "url": _GN_BASE + "教員+学校+先生+-コラム",
        "source_type": "Google News",
        "source_name": "Google News（教員・学校）",
        "priority": 1,
    },
    # ② 教員不足・働き方（社会問題系）
    {
        "url": _GN_BASE + "教員不足+給特法+学校",
        "source_type": "Google News",
        "source_name": "Google News（教員不足）",
        "priority": 2,
    },
    # ③ 不登校・いじめ
    {
        "url": _GN_BASE + "不登校+いじめ+学校",
        "source_type": "Google News",
        "source_name": "Google News（不登校・いじめ）",
        "priority": 3,
    },
    # ④ 保護者・PTA・学校制度
    {
        "url": _GN_BASE + "保護者+PTA+学校+教育委員会",
        "source_type": "Google News",
        "source_name": "Google News（保護者・制度）",
        "priority": 4,
    },
    # ⑤ 部活・特別支援・GIGAスクール
    {
        "url": _GN_BASE + "部活+特別支援+GIGAスクール",
        "source_type": "Google News",
        "source_name": "Google News（部活・ICT）",
        "priority": 5,
    },
]

# ── ジャンルタグ推定：タイトル・本文のキーワードからマッピング ──────────────
_GENRE_MAP: dict[str, list[str]] = {
    "教員不足":     ["教員不足", "代替教員", "人手不足", "欠員", "担任不在", "定員割れ"],
    "働き方":       ["残業", "長時間労働", "給特法", "働き方", "過労", "休暇", "業務削減", "時間外"],
    "学校制度":     ["文科省", "教育委員会", "学習指導要領", "制度改革", "教育政策", "通知"],
    "保護者対応":   ["保護者", "クレーム", "PTA", "モンペ", "家庭", "連絡帳", "面談"],
    "学級経営":     ["学級", "クラス", "学級経営", "担任", "学級崩壊", "授業規律"],
    "不登校":       ["不登校", "登校拒否", "引きこもり", "別室登校", "フリースクール"],
    "メンタルヘルス": ["メンタル", "うつ", "精神", "ストレス", "燃え尽き", "心の健康", "病気休暇"],
    "部活":         ["部活", "クラブ", "地域移行", "顧問", "休日指導", "部活動"],
    "特別支援":     ["特別支援", "インクルーシブ", "発達障害", "ADHD", "通級", "合理的配慮"],
    "GIGAスクール": ["GIGA", "ICT", "タブレット", "デジタル", "端末", "オンライン授業"],
    "新年度":       ["新年度", "新学期", "春", "入学", "始業式", "学級開き"],
    "教員採用":     ["教員採用", "採用試験", "倍率", "教員志望", "なり手不足"],
    "給食":         ["給食", "食育", "アレルギー", "栄養士"],
}


def _infer_genre_tags(title: str, summary: str = "") -> list[str]:
    """タイトル＋概要からジャンルタグを推定する"""
    text = f"{title} {summary}"
    tags = [genre for genre, kws in _GENRE_MAP.items() if any(kw in text for kw in kws)]
    # タグが付かなかった場合の汎用タグ
    if not tags:
        tags = ["教育全般"]
    return tags[:4]  # 最大4つまで


def _parse_published(entry: feedparser.FeedParserDict) -> str:
    """feedparser エントリから公開日時を ISO 文字列で返す（フォールバック付き）"""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            return dt.astimezone(JST).date().isoformat()
        except Exception:
            pass
    return date.today().isoformat()


def _entry_to_news_item(entry: feedparser.FeedParserDict, feed_meta: dict) -> dict:
    """feedparser エントリを html_report.py が期待する dict に変換"""
    title = entry.get("title", "（タイトルなし）").strip()
    url = entry.get("link", "")
    summary = entry.get("summary", entry.get("description", "")).strip()
    # HTML タグを簡易除去
    import re
    summary = re.sub(r"<[^>]+>", "", summary)[:200]

    genre_tags = _infer_genre_tags(title, summary)
    published_at = _parse_published(entry)

    # 記事IDはURLのハッシュで生成（重複排除に使用）
    item_id = "rss_" + hashlib.md5(url.encode()).hexdigest()[:8]

    return {
        "id": item_id,
        "title": title,
        "url": url,
        "source_type": feed_meta["source_type"],
        "source_name": feed_meta["source_name"],
        "published_at": published_at,
        "genre_tags": genre_tags,
        "summary": summary,
        "trend_score": 0,       # scorer.py で上書きされる
        "emotions": [],         # scorer / AI で補完
        "connection_score": 3,
        "formats": [],
        "angle_memo": "",       # AI で補完
        "caution_level": "中",
        "caution_reason": "",
        "x_rt_count": 0,
        "x_like_count": 0,
        "_priority": feed_meta["priority"],
    }


def fetch_rss_news(
    max_per_feed: int = 20,
    timeout: int = 10,
) -> list[dict]:
    """
    全 RSS フィードを取得し、重複排除済みの記事リストを返す。

    Parameters
    ----------
    max_per_feed : 1フィードあたり最大取得件数
    timeout      : HTTP タイムアウト（秒）

    Returns
    -------
    list[dict]  ─ mock_news.py と同じキー構造
    """
    all_items: list[dict] = []
    seen_urls: set[str] = set()

    for feed_meta in RSS_FEEDS:
        feed_url = feed_meta["url"]
        try:
            # feedparser は内部で requests を使わないので timeout を渡せない
            # → requests で先に取得して feedparser に渡す
            resp = requests.get(feed_url, timeout=timeout, headers={
                "User-Agent": "Mozilla/5.0 (compatible; EducationReportBot/1.0)"
            })
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
        except Exception as e:
            logger.warning("RSS 取得失敗 [%s]: %s", feed_url, e)
            continue

        count = 0
        for entry in feed.entries:
            if count >= max_per_feed:
                break
            url = entry.get("link", "")
            if not url or url in seen_urls:
                continue
            item = _entry_to_news_item(entry, feed_meta)
            all_items.append(item)
            seen_urls.add(url)
            count += 1

        logger.info("フィード取得完了 [%s]: %d件", feed_meta["source_name"], count)

    logger.info("RSS合計取得件数（重複排除後）: %d件", len(all_items))
    return all_items
