"""
教育ニュース フィルタリングモジュール

優先度：
  高 → 教育新聞・地方紙のストレートニュース
  低 → コラム・社説・オピニオン・広告・PR記事
"""
import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)

# ── 除外ワード（コラム・意見・PR系） ─────────────────────────────────────────
_EXCLUDE_TITLE_WORDS: list[str] = [
    "コラム", "社説", "論説", "オピニオン", "読者投稿", "読者の声",
    "記者の目", "記者コラム", "論評", "書評", "PR", "広告", "提供",
    "特集広告", "タイアップ", "ランキング", "占い", "クイズ",
    "訃報", "おくやみ", "人事", "訂正", "おわび",
]

# 教育ニュースとして採用する必須キーワード（いずれか1つ含まれていればOK）
_EDUCATION_KEYWORDS: list[str] = [
    "教員", "教師", "先生", "学校", "文科省", "教育委員会",
    "生徒", "児童", "学級", "担任", "授業", "部活", "不登校",
    "保護者", "PTA", "給食", "クラス", "入学", "卒業", "校長",
    "学習", "GIGAスクール", "ICT", "特別支援", "発達障害",
    "教員採用", "教育改革", "給特法", "残業", "長時間労働",
    "いじめ", "体罰", "教員不足", "子ども", "子供", "子育て",
    "幼稚園", "保育", "小学校", "中学校", "高校", "大学",
    "教育", "文部科学", "塾", "習い事", "放課後", "夏休み",
]

# ── 重要度ブースト：このワードが含まれると優先度を上げる ─────────────────────
_HIGH_PRIORITY_WORDS: list[str] = [
    "教員不足", "給特法", "不登校", "いじめ", "部活", "長時間労働",
    "学級崩壊", "保護者", "教員採用", "代替教員", "メンタル",
]

# 何日前までの記事を有効とするか（Google Newsは古い記事も返すことがある）
_MAX_AGE_DAYS: int = 14


def _is_too_old(item: dict) -> bool:
    published = item.get("published_at", "")
    if not published:
        return False
    try:
        pub_date = date.fromisoformat(published)
        return (date.today() - pub_date).days > _MAX_AGE_DAYS
    except ValueError:
        return False


def _is_column(title: str) -> bool:
    """コラム・社説などの非ストレートニュースを判定"""
    return any(w in title for w in _EXCLUDE_TITLE_WORDS)


def _is_education_related(title: str, summary: str = "") -> bool:
    """教育関連の記事か判定"""
    text = f"{title} {summary}"
    return any(kw in text for kw in _EDUCATION_KEYWORDS)


def _boost_score(item: dict) -> int:
    """重要度ブーストスコアを計算（ソート用）"""
    title = item.get("title", "")
    return sum(1 for w in _HIGH_PRIORITY_WORDS if w in title)


def filter_education_news(
    items: list[dict],
    max_items: int = 30,
) -> list[dict]:
    """
    RSS から取得した記事リストを教育ニュースとしてフィルタリング・ランク付けして返す。

    Parameters
    ----------
    items     : rss_fetcher.fetch_rss_news() の返り値
    max_items : 最終的に返す最大件数

    Returns
    -------
    list[dict]  ─ フィルタ済み・優先度順でソートされた記事リスト
    """
    filtered: list[dict] = []
    excluded_count = 0

    for item in items:
        title = item.get("title", "")
        summary = item.get("summary", "")
        source_type = item.get("source_type", "")

        # ① コラム・社説を除外（全ソース共通）
        if _is_column(title):
            logger.debug("コラム除外: %s", title[:40])
            excluded_count += 1
            continue

        # ② 古すぎる記事を除外（全ソース共通）
        if _is_too_old(item):
            logger.debug("古い記事除外: %s", title[:40])
            excluded_count += 1
            continue

        # ③ 教育関連チェック
        #    Google News はキーワード検索済みなのでスキップ
        if source_type != "Google News" and not _is_education_related(title, summary):
            logger.debug("教育無関係除外: %s", title[:40])
            excluded_count += 1
            continue

        filtered.append(item)

    logger.info(
        "フィルタ結果: %d件採用 / %d件除外（合計%d件）",
        len(filtered), excluded_count, len(filtered) + excluded_count,
    )

    # ── ソート基準 ──────────────────────────────────────────────────────────
    # 1. 重要キーワードのブーストスコア（高いほど上）
    # 2. ソース優先度（_priority が低いほど優先）
    # 3. 公開日（新しいほど上）
    filtered.sort(
        key=lambda x: (
            -_boost_score(x),               # 重要ワード多いほど上
            x.get("_priority", 99),         # ソース優先度
            x.get("published_at", "") or "", # 新しい順（文字列比較で降順にするため反転できないのでキー工夫）
        ),
        reverse=False,
    )
    # published_at だけ降順にしたいので、同順位内で新しいものが上になるよう再ソート
    filtered.sort(
        key=lambda x: (
            -_boost_score(x),
            x.get("_priority", 99),
            -(int(x.get("published_at", "2000-01-01").replace("-", "")) if x.get("published_at") else 0),
        )
    )

    return filtered[:max_items]
