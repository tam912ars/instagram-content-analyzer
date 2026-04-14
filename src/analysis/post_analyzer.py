"""投稿・コメントの分析モジュール"""
import re
from collections import Counter
from datetime import datetime
from typing import Any

import pandas as pd


STOP_WORDS = {
    "の", "に", "は", "を", "が", "で", "と", "た", "し", "て",
    "い", "な", "か", "も", "れ", "さ", "っ", "ん", "す", "こ",
    "ます", "です", "から", "ので", "ない", "ある", "いる", "する",
    "なる", "られ", "られる", "ため", "こと", "もの", "それ", "これ",
    "あの", "その", "http", "https", "www", "com",
}


def parse_posts(raw_posts: list[dict]) -> pd.DataFrame:
    """生データをDataFrameに変換"""
    records = []
    for post in raw_posts:
        ts = post.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            dt = datetime.now()

        records.append({
            "id": post.get("id", ""),
            "caption": post.get("caption", ""),
            "media_type": post.get("media_type", "IMAGE"),
            "timestamp": dt,
            "like_count": int(post.get("like_count", 0)),
            "comments_count": int(post.get("comments_count", 0)),
            "comments": post.get("comments", []),
            "engagement": int(post.get("like_count", 0)) + int(post.get("comments_count", 0)) * 3,
        })

    df = pd.DataFrame(records)
    if not df.empty:
        df = df.sort_values("timestamp", ascending=False).reset_index(drop=True)
    return df


def extract_keywords(texts: list[str], top_n: int = 20) -> list[tuple[str, int]]:
    """テキストリストからキーワードを抽出"""
    words = []
    for text in texts:
        text = re.sub(r"[#＃@＠！!。、\.,%&\(\)\[\]「」『』【】\n\r\t]", " ", text)
        tokens = re.split(r"\s+", text)
        for token in tokens:
            token = token.strip()
            if len(token) >= 2 and token not in STOP_WORDS and not token.isdigit():
                words.append(token)

    counter = Counter(words)
    return counter.most_common(top_n)


def extract_hashtags(captions: list[str]) -> list[tuple[str, int]]:
    """ハッシュタグを抽出して集計"""
    tags = []
    for caption in captions:
        found = re.findall(r"[#＃](\w+)", caption)
        tags.extend(found)
    return Counter(tags).most_common(20)


def get_top_posts(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """エンゲージメント上位の投稿を返す"""
    return df.nlargest(n, "engagement")[["caption", "media_type", "like_count", "comments_count", "engagement", "timestamp"]]


def get_comment_keywords(posts: list[dict], top_n: int = 20) -> list[tuple[str, int]]:
    """全コメントからキーワードを抽出"""
    all_comments = []
    for post in posts:
        for comment in post.get("comments", []):
            text = comment.get("text", "")
            if text:
                all_comments.append(text)
    return extract_keywords(all_comments, top_n=top_n)


def get_post_type_breakdown(df: pd.DataFrame) -> dict[str, Any]:
    """投稿タイプ別（フィード/リール）の集計"""
    if df.empty:
        return {}
    grouped = df.groupby("media_type").agg(
        count=("id", "count"),
        avg_likes=("like_count", "mean"),
        avg_comments=("comments_count", "mean"),
        avg_engagement=("engagement", "mean"),
    ).reset_index()
    return grouped.to_dict(orient="records")


def get_engagement_trend(df: pd.DataFrame) -> pd.DataFrame:
    """時系列のエンゲージメント推移"""
    if df.empty:
        return df
    df = df.copy()
    df["date"] = df["timestamp"].dt.date
    trend = df.groupby("date").agg(
        avg_engagement=("engagement", "mean"),
        post_count=("id", "count"),
    ).reset_index()
    return trend.sort_values("date")


def get_frequently_asked_questions(posts: list[dict]) -> list[str]:
    """質問系コメントを抽出（？マークを含む）"""
    questions = []
    for post in posts:
        for comment in post.get("comments", []):
            text = comment.get("text", "")
            if "?" in text or "？" in text or "ですか" in text or "でしょうか" in text:
                questions.append(text.strip())
    return questions[:20]
