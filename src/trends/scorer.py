"""ネタスコアリング＆今日のTOP3選定モジュール"""
from datetime import date, datetime
import math


# ─── 季節タグマッピング（月 → 旬のキーワード）
SEASONAL_KEYWORDS: dict[int, list[str]] = {
    1: ["新年", "目標", "リセット", "冬"],
    2: ["節分", "受験", "春へ向けて"],
    3: ["年度末", "卒業", "お別れ", "振り返り"],
    4: ["新年度", "学級開き", "新任", "新生活", "スタート", "部活", "出会い"],
    5: ["GW", "5月病", "連休", "中だるみ"],
    6: ["梅雨", "体力測定", "運動会"],
    7: ["夏休み", "熱中症", "期末"],
    8: ["夏", "宿題", "夏休み", "自由研究"],
    9: ["2学期", "運動会", "文化祭", "秋"],
    10: ["体育祭", "修学旅行", "ハロウィン"],
    11: ["進路", "受験勉強", "授業参観"],
    12: ["冬休み", "学期末", "大掃除", "振り返り"],
}


def _seasonal_score(genre_tags: list[str], title: str, month: int) -> float:
    """季節一致スコア（0〜1）"""
    seasonal_kw = SEASONAL_KEYWORDS.get(month, [])
    text = " ".join(genre_tags) + " " + title
    hits = sum(1 for kw in seasonal_kw if kw in text)
    return min(hits / max(len(seasonal_kw) * 0.3, 1), 1.0)


def _news_connection_score(news_item: dict) -> float:
    """外部ニュースとの接続しやすさスコア（0〜1）"""
    raw = news_item.get("connection_score", 1)
    return (raw - 1) / 4.0  # 1〜5を0〜1に


def _comment_heat_score(comment_keywords: list[tuple[str, int]], genre_tags: list[str], title: str) -> float:
    """自分のコメントキーワードとの一致スコア（0〜1）"""
    if not comment_keywords:
        return 0.0
    text = " ".join(genre_tags) + " " + title
    total_weight = sum(count for _, count in comment_keywords)
    hit_weight = sum(count for kw, count in comment_keywords if kw in text)
    return min(hit_weight / max(total_weight * 0.05, 1), 1.0)


def _external_trend_score(news_item: dict) -> float:
    """話題度スコア（0〜1）"""
    return news_item.get("trend_score", 0) / 100.0


def _past_performance_score(past_post_captions: list[str], genre_tags: list[str], title: str) -> float:
    """過去の伸びた投稿との類似スコア（0〜1）"""
    if not past_post_captions:
        return 0.3
    text = " ".join(genre_tags) + " " + title
    hits = sum(1 for cap in past_post_captions[:10] if any(tag in cap for tag in genre_tags))
    return min(hits / 5.0, 1.0)


def score_news_item(
    news_item: dict,
    comment_keywords: list[tuple[str, int]],
    past_post_captions: list[str],
    today: date = None,
) -> dict:
    """ニュースアイテムの総合スコアを計算して返す"""
    if today is None:
        today = date.today()
    month = today.month

    genre_tags = news_item.get("genre_tags", [])
    title = news_item.get("title", "")

    w_seasonal = 0.20
    w_news = 0.25
    w_comment = 0.20
    w_external = 0.20
    w_past = 0.15

    s_seasonal = _seasonal_score(genre_tags, title, month)
    s_news = _news_connection_score(news_item)
    s_comment = _comment_heat_score(comment_keywords, genre_tags, title)
    s_external = _external_trend_score(news_item)
    s_past = _past_performance_score(past_post_captions, genre_tags, title)

    total = (
        w_seasonal * s_seasonal
        + w_news * s_news
        + w_comment * s_comment
        + w_external * s_external
        + w_past * s_past
    ) * 100

    return {
        **news_item,
        "composite_score": round(total, 1),
        "score_breakdown": {
            "seasonal": round(s_seasonal * 100),
            "news_connection": round(s_news * 100),
            "comment_heat": round(s_comment * 100),
            "external_trend": round(s_external * 100),
            "past_performance": round(s_past * 100),
        },
    }


def get_top3_content_ideas(
    news_items: list[dict],
    comment_keywords: list[tuple[str, int]],
    past_post_captions: list[str],
    today: date = None,
) -> list[dict]:
    """今日いちばん伸びそうなネタ TOP3 を選定して返す"""
    if today is None:
        today = date.today()

    scored = [
        score_news_item(item, comment_keywords, past_post_captions, today)
        for item in news_items
    ]
    scored.sort(key=lambda x: x["composite_score"], reverse=True)
    return scored[:3]


def get_dual_summary(
    comment_keywords: list[tuple[str, int]],
    news_items: list[dict],
    today: date = None,
) -> dict:
    """ファーストビュー用のデュアルサマリーを生成"""
    if today is None:
        today = date.today()

    # フォロワー反応トップ3キーワード
    follower_topics = [kw for kw, _ in comment_keywords[:5]]

    # 外部ニューストップ3（話題度順）
    sorted_news = sorted(news_items, key=lambda x: x.get("trend_score", 0), reverse=True)
    external_topics = [item["title"][:30] + "…" for item in sorted_news[:3]]

    # 感情傾向サマリー
    all_emotions: dict[str, float] = {}
    for item in news_items:
        for em in item.get("emotions", []):
            t = em["type"]
            all_emotions[t] = all_emotions.get(t, 0) + em["intensity"]
    dominant_emotion = max(all_emotions, key=lambda k: all_emotions[k]) if all_emotions else "不明"

    # 今月の旬キーワード
    seasonal_kw = SEASONAL_KEYWORDS.get(today.month, [])

    return {
        "date": today.strftime("%Y年%m月%d日"),
        "follower_topics": follower_topics,
        "external_topics": external_topics,
        "dominant_emotion": dominant_emotion,
        "seasonal_keywords": seasonal_kw[:4],
        "top_news_score": sorted_news[0]["trend_score"] if sorted_news else 0,
        "top_news_title": sorted_news[0]["title"] if sorted_news else "",
    }
