"""
教育ニュース フィルタリングモジュール

ターゲット：現役教師・教員志望者
優先テーマ：働き方・教員不足・部活改革・学校制度・ICT・メンタル
低優先：いじめ・不登校（保護者向けが多いため）
コラム：一部採用OK（教師視点のものは有益）
"""
import logging
from datetime import date

logger = logging.getLogger(__name__)

# ── 完全除外（広告・PR・無関係） ─────────────────────────────────────────────
_HARD_EXCLUDE: list[str] = [
    "PR", "広告", "提供", "特集広告", "タイアップ",
    "訃報", "おくやみ", "人事", "訂正", "おわび",
    "占い", "クイズ", "ランキング", "まとめ",
    "社説", "論説",  # 意見記事は除外
]

# ── 教師向け優先キーワード（ブーストスコアが高いほど上位に） ────────────────
_TEACHER_PRIORITY: list[tuple[str, int]] = [
    # スコア3：教師が直接関係する最重要テーマ
    ("給特法", 3), ("教員不足", 3), ("教員採用", 3),
    ("部活動", 3), ("地域移行", 3), ("残業代", 3),
    ("時間外労働", 3), ("病気休職", 3), ("メンタルヘルス", 3),
    ("バーンアウト", 3), ("働き方改革", 3), ("学級崩壊", 3),
    # スコア2：教師の日常業務に関わるテーマ
    ("GIGAスクール", 2), ("ICT", 2), ("AI", 2),
    ("特別支援", 2), ("インクルーシブ", 2), ("発達障害", 2),
    ("教員研修", 2), ("免許更新", 2), ("初任者", 2),
    ("学習指導要領", 2), ("教育委員会", 2), ("文科省", 2),
    # スコア1：間接的に関わるテーマ
    ("教員", 1), ("教師", 1), ("先生", 1), ("担任", 1),
    ("授業", 1), ("学級", 1), ("校長", 1), ("副校長", 1),
]

# ── 保護者向けキーワード（採用するが優先度を下げる） ─────────────────────────
_PARENT_FOCUSED: list[str] = [
    "いじめ", "不登校", "保護者", "PTA", "モンペ",
    "給食費", "学費", "受験", "塾", "習い事",
]

# 教育ニュースとして採用する必須キーワード
_EDUCATION_KEYWORDS: list[str] = [
    "教員", "教師", "先生", "学校", "文科省", "教育委員会",
    "生徒", "児童", "学級", "担任", "授業", "部活",
    "給食", "クラス", "入学", "卒業", "校長",
    "GIGAスクール", "ICT", "特別支援", "発達障害",
    "教員採用", "教育改革", "給特法", "長時間労働",
    "教育", "文部科学", "小学校", "中学校", "高校",
    "不登校", "いじめ", "保護者", "子ども",
]

# 何日前までの記事を有効とするか
# Google Newsは構造的な問題（給特法・教員不足など）の記事も返すため緩めに設定
_MAX_AGE_DAYS: int = 90


def _is_too_old(item: dict) -> bool:
    published = item.get("published_at", "")
    if not published:
        return False
    try:
        pub_date = date.fromisoformat(published)
        return (date.today() - pub_date).days > _MAX_AGE_DAYS
    except ValueError:
        return False


def _is_hard_excluded(title: str) -> bool:
    """広告・PR・無関係を完全除外"""
    return any(w in title for w in _HARD_EXCLUDE)


def _is_education_related(title: str, summary: str = "") -> bool:
    text = f"{title} {summary}"
    return any(kw in text for kw in _EDUCATION_KEYWORDS)


def _teacher_score(item: dict) -> int:
    """教師向けスコアを計算（高いほど優先）"""
    text = item.get("title", "") + " " + item.get("summary", "")
    score = sum(pts for kw, pts in _TEACHER_PRIORITY if kw in text)
    # 保護者向けワードが多い記事はスコアを下げる
    parent_hits = sum(1 for w in _PARENT_FOCUSED if w in text)
    score -= parent_hits
    return score


def _is_duplicate(title: str, seen_titles: list[str], threshold: float = 0.65) -> bool:
    """タイトルの単語一致率で同一事件の記事を判定"""
    words = set(title.replace("　", " ").split())
    if not words:
        return False
    for seen in seen_titles:
        seen_words = set(seen.replace("　", " ").split())
        if not seen_words:
            continue
        overlap = len(words & seen_words) / max(len(words), len(seen_words))
        if overlap >= threshold:
            return True
    return False


def filter_education_news(
    items: list[dict],
    max_items: int = 20,
) -> list[dict]:
    """
    RSS記事を教師向けにフィルタリング・ランク付けして返す。

    - 広告・PR・社説は完全除外
    - コラムは一部採用（教師視点のものは有益）
    - いじめ・不登校は採用するが優先度を下げる
    - 同一事件の記事は最上位1件のみ採用
    """
    filtered: list[dict] = []
    excluded_count = 0
    source_type_count: dict[str, int] = {}  # フィードごとの採用数制限

    for item in items:
        title = item.get("title", "")
        summary = item.get("summary", "")
        source_name = item.get("source_name", "")
        source_type = item.get("source_type", "")

        # ① 広告・PR・社説を完全除外
        if _is_hard_excluded(title):
            excluded_count += 1
            continue

        # ② 古すぎる記事を除外
        if _is_too_old(item):
            excluded_count += 1
            continue

        # ③ 教育関連チェック（Google Newsはクエリ済みなのでスキップ）
        if source_type != "Google News" and not _is_education_related(title, summary):
            excluded_count += 1
            continue

        # ④ 同一フィードから最大5件まで（1テーマに偏らないように）
        count = source_type_count.get(source_name, 0)
        if count >= 5:
            excluded_count += 1
            continue
        source_type_count[source_name] = count + 1

        filtered.append(item)

    logger.info(
        "フィルタ結果: %d件採用 / %d件除外（合計%d件）",
        len(filtered), excluded_count, len(filtered) + excluded_count,
    )

    # ── 教師向けスコアでソート ───────────────────────────────────────────────
    filtered.sort(
        key=lambda x: (
            -_teacher_score(x),
            x.get("_priority", 99),
            -(int(x.get("published_at", "2000-01-01").replace("-", ""))
              if x.get("published_at") else 0),
        )
    )

    # ── 同一事件の記事を1件に絞る ────────────────────────────────────────────
    deduplicated: list[dict] = []
    seen_titles: list[str] = []
    for item in filtered:
        title = item.get("title", "")
        if not _is_duplicate(title, seen_titles):
            deduplicated.append(item)
            seen_titles.append(title)

    logger.info("重複除去後: %d件", len(deduplicated))
    return deduplicated[:max_items]
