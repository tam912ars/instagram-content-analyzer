"""Instagram Graph API クライアント"""
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

CACHE_DIR = Path(__file__).parent.parent.parent / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://graph.instagram.com/v19.0"


class InstagramClient:
    def __init__(self):
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
        self.account_id = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
        self.cache_hours = int(os.getenv("CACHE_HOURS", "6"))

    def _cache_path(self, key: str) -> Path:
        return CACHE_DIR / f"{key}.json"

    def _load_cache(self, key: str) -> Optional[dict]:
        path = self._cache_path(key)
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            cached = json.load(f)
        expires_at = datetime.fromisoformat(cached["expires_at"])
        if datetime.now() > expires_at:
            return None
        return cached["data"]

    def _save_cache(self, key: str, data: dict) -> None:
        expires_at = datetime.now() + timedelta(hours=self.cache_hours)
        with open(self._cache_path(key), "w", encoding="utf-8") as f:
            json.dump({"expires_at": expires_at.isoformat(), "data": data}, f, ensure_ascii=False, indent=2)

    def _get(self, endpoint: str, params: dict = None) -> dict:
        if params is None:
            params = {}
        params["access_token"] = self.access_token
        response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_posts(self, limit: int = 50, use_cache: bool = True) -> list[dict]:
        """投稿一覧を取得（キャプション・タイムスタンプ・エンゲージメント含む）"""
        cache_key = f"posts_{limit}"
        if use_cache:
            cached = self._load_cache(cache_key)
            if cached:
                return cached

        fields = "id,caption,media_type,timestamp,like_count,comments_count,thumbnail_url,media_url"
        data = self._get(
            f"{self.account_id}/media",
            {"fields": fields, "limit": limit}
        )
        posts = data.get("data", [])
        self._save_cache(cache_key, posts)
        return posts

    def get_comments(self, post_id: str, use_cache: bool = True) -> list[dict]:
        """特定投稿のコメントを取得"""
        cache_key = f"comments_{post_id}"
        if use_cache:
            cached = self._load_cache(cache_key)
            if cached:
                return cached

        fields = "id,text,timestamp,like_count,username"
        data = self._get(
            f"{post_id}/comments",
            {"fields": fields, "limit": 100}
        )
        comments = data.get("data", [])
        self._save_cache(cache_key, comments)
        return comments

    def get_all_posts_with_comments(self, max_posts: int = 30, use_cache: bool = True) -> list[dict]:
        """投稿＋コメントをまとめて取得"""
        posts = self.get_posts(limit=max_posts, use_cache=use_cache)
        for post in posts:
            post["comments"] = self.get_comments(post["id"], use_cache=use_cache)
            time.sleep(0.2)
        return posts

    def get_account_insights(self, use_cache: bool = True) -> dict:
        """アカウント全体のインサイト取得"""
        cache_key = "account_insights"
        if use_cache:
            cached = self._load_cache(cache_key)
            if cached:
                return cached

        fields = "followers_count,follows_count,media_count,biography,name,username"
        data = self._get(self.account_id, {"fields": fields})
        self._save_cache(cache_key, data)
        return data
