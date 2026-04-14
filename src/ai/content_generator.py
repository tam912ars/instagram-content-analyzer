"""GPT-4o を使ったコンテンツ案生成モジュール"""
import json
import logging
import os
from datetime import date

from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ContentGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")

    def _chat(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.8,
            )
            return response.choices[0].message.content.strip()
        except OpenAIError as e:
            logger.error("OpenAI API エラー: %s", e)
            raise RuntimeError(f"OpenAI API 呼び出し失敗: {e}") from e

    def generate_daily_report(
        self,
        top_posts: list[dict],
        comment_keywords: list[tuple[str, int]],
        questions: list[str],
        hashtags: list[tuple[str, int]],
        today: date = None,
    ) -> dict:
        """毎日のコンテンツ提案レポートを生成"""
        if today is None:
            today = date.today()

        system_prompt = """あなたはInstagramのコンテンツ戦略の専門家です。
現役教員パパとして学校・教育・先生の働き方を発信する「ダイ先生」（@dy.papa_teacher）の
Instagramデータを分析し、魅力的なコンテンツ案を提案してください。

発信テーマ：学級経営、保護者対応、教員の働き方、不登校対応、部活問題、
職員室のリアル、新年度の準備、子どもとの関わり方、特別支援、教員採用 など

提案は必ずJSON形式で返してください。"""

        kw_text = ", ".join([f"{w}({c}回)" for w, c in comment_keywords[:10]])
        q_text = "\n".join([f"- {q}" for q in questions[:10]])
        tag_text = ", ".join([f"#{t}({c})" for t, c in hashtags[:10]])

        top_post_text = ""
        for i, p in enumerate(top_posts[:3], 1):
            caption = str(p.get("caption", ""))[:80]
            top_post_text += f"{i}. {caption}... (いいね:{p.get('like_count',0)}, コメント:{p.get('comments_count',0)})\n"

        user_prompt = f"""
今日の日付: {today.strftime('%Y年%m月%d日')}

【エンゲージメント上位の投稿】
{top_post_text}

【コメントで多いキーワード】
{kw_text}

【よく寄せられる質問】
{q_text}

【よく使われるハッシュタグ】
{tag_text}

上記のデータをもとに、以下のJSON形式で今日のコンテンツ案を提案してください。
フィードとリールは分けず「Instagram用」としてまとめて提案してください。

{{
  "date": "YYYY年MM月DD日",
  "summary": "今日のデータから見えるトレンドの一言まとめ",
  "instagram_ideas": [
    {{
      "title": "投稿タイトル案",
      "format_suggestion": "フィード推奨 or リール推奨 or どちらでもOK",
      "format_reason": "その形式を推奨する理由",
      "hook": "冒頭1行（読者を引きつけるフック）",
      "body_points": ["本文のポイント1", "ポイント2", "ポイント3"],
      "caption_template": "キャプションのテンプレート文",
      "hashtags": ["#タグ1", "#タグ2"],
      "reason": "このネタを提案する理由（データとの関連性）"
    }}
  ],
  "stafy_topics": [
    {{
      "title": "スタエフのトークタイトル",
      "opening": "冒頭のトーク案",
      "talk_points": ["トークポイント1", "トークポイント2", "トークポイント3"],
      "closing": "締めのトーク案",
      "estimated_minutes": 15,
      "reason": "このネタを提案する理由"
    }}
  ],
  "youtube_live_topics": [
    {{
      "title": "YouTubeライブのタイトル案",
      "description": "概要文",
      "agenda": ["アジェンダ1", "アジェンダ2", "アジェンダ3"],
      "q_and_a_seeds": ["想定される質問1", "想定される質問2"],
      "recommended_duration_min": 60,
      "reason": "このネタを提案する理由"
    }}
  ],
  "insights": [
    "データから読み取れるインサイト1",
    "インサイト2",
    "インサイト3"
  ]
}}

Instagram案3件、スタエフ案2件、YouTubeライブ案1件を提案してください。
"""

        try:
            raw = self._chat(system_prompt, user_prompt)
        except RuntimeError as e:
            return {"error": str(e)}

        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.error("JSON解析失敗。rawレスポンスの先頭: %.200s", raw)
            return {"error": "JSON解析エラー", "raw": raw}
