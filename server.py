"""
ダイ先生 コンテンツ分析ダッシュボード - Flask サーバー
Tailwind CSS の HTML をそのまま配信する
"""
import sys, os, time, threading
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, redirect, url_for
from src.visualization.html_report import generate_html_report
from src.trends.mock_news import get_mock_news
from src.trends.mock_comments import get_mock_hot_comments
from src.trends.mock_past_posts import get_mock_past_posts
from src.trends.scorer import get_top3_content_ideas, get_dual_summary, score_news_item
from src.instagram.mock_data import generate_mock_posts, generate_mock_account
from src.analysis.post_analyzer import parse_posts, get_comment_keywords, extract_hashtags

app = Flask(__name__)

# ── インメモリキャッシュ（TTL: 10分）
_CACHE: dict = {"html": None, "ts": 0.0}
_CACHE_TTL = 600  # 秒
_CACHE_LOCK = threading.Lock()


def _build_report_html() -> str:
    """モックデータからHTMLレポートを生成"""
    raw_posts = generate_mock_posts(20)
    account = generate_mock_account()
    df = parse_posts(raw_posts)
    captions = df["caption"].tolist()
    comment_keywords = get_comment_keywords(raw_posts, top_n=20)
    hashtags = extract_hashtags(captions)

    news_items = get_mock_news()
    scored_news = [score_news_item(item, comment_keywords, captions) for item in news_items]
    scored_news_sorted = sorted(scored_news, key=lambda x: x.get("trend_score", 0), reverse=True)
    top3 = get_top3_content_ideas(news_items, comment_keywords, captions)
    dual = get_dual_summary(comment_keywords, news_items)

    # ダッシュボード用のモックレポートデータ（GPT不要）
    mock_ai_report = {
        "date": __import__("datetime").date.today().strftime("%Y年%m月%d日"),
        "summary": "「学級開き」「保護者対応」に関するコメントと外部ニュース（新年度・教員不足）が完全連動。4月の今が最高のタイミングです。",
        "insights": [
            "4月の新年度タイミングで「学級開き」「新任教員」関連ニュースが急増 — 今週の投稿最優先テーマ",
            "「スタエフで聞きました」コメントが増加傾向 — クロスメディア施策が効いている",
            "保護者対応・不登校対応への質問コメントが多く、実践的ノウハウ系の保存率が高い",
        ],
        "instagram_ideas": [
            {
                "title": "学級開きで「絶対やってはいけないこと」3選",
                "format_suggestion": "フィード推奨",
                "format_reason": "リスト形式で保存率が高く、同僚への拡散も起きやすい",
                "hook": "4月の学級開きで失敗した先生が共通してやっていた「あること」がある。",
                "body_points": [
                    "ルール説明から始めてしまう（子どもが心を開く前にシャッターが下りる）",
                    "担任の自己紹介を長くしすぎる（最初の印象は「この先生大丈夫？」）",
                    "最初の日に宿題を出す（信頼関係ゼロの状態でのプレッシャーはNG）",
                ],
                "caption_template": "【学級開きで絶対やってはいけないこと3選】\n\n毎年4月に同じ失敗をしている先生がいます。\nその共通点をまとめました。\n\n新年度を迎えるすべての先生へ🍀\n\n#学級経営 #新年度 #学級開き #先生 #教員 #教育",
                "hashtags": ["#学級経営", "#新年度", "#学級開き", "#先生", "#教員"],
                "reason": "「学級開き」関連ニュースとコメントが4月に急増。失敗談は共感・保存・シェアの三拍子が揃う。",
            },
            {
                "title": "保護者からのクレーム、最初の30秒で決まる対応術",
                "format_suggestion": "リール推奨",
                "format_reason": "ロールプレイ形式でリアルな対話を再現でき、視覚的に伝わりやすい",
                "hook": "クレーム対応が上手い先生は、最初の30秒で必ずこれをやっている。",
                "body_points": [
                    "まず「ご連絡いただきありがとうございます」で始める（防衛反応を下げる）",
                    "「おっしゃる通りです」は使わない（事実確認前の同意はNG）",
                    "「一度確認させてください」で時間を作る（感情的な場面では即答しない）",
                ],
                "caption_template": "【保護者クレーム対応、最初の30秒が全て】\n\n学校ではなぜか教えてもらえないこの技術。\n現場で使える言葉をそのまま紹介します。\n\n#保護者対応 #学級経営 #先生あるある #教員の働き方 #教育",
                "hashtags": ["#保護者対応", "#学級経営", "#先生あるある", "#教員の働き方"],
                "reason": "「保護者対応についてもっと教えてください」というコメントが多い。具体的すぎるくらいの実践ネタが最も保存される。",
            },
            {
                "title": "新年度の職員室、先生の本音をぶっちゃける",
                "format_suggestion": "どちらでもOK",
                "format_reason": "テキスト系ならフィード、語りならリール。どちらも高反応が見込める",
                "hook": "「おはようございます」って言うのが、4月だけ少し怖い。",
                "body_points": [
                    "新しい管理職・同僚との距離感がわからない最初の1週間",
                    "笑顔でいないといけない空気の中で疲弊する本音",
                    "それでも「子どもたちのためにやろう」と思える理由",
                ],
                "caption_template": "【新年度の職員室、先生の本音】\n\n外からは見えない4月の職員室のリアルを話します。\nこれを読んで「私だけじゃなかった」って思えたら嬉しい。\n\n#先生あるある #職員室 #新年度 #教員 #先生の本音",
                "hashtags": ["#先生あるある", "#職員室", "#新年度", "#教員", "#先生の本音"],
                "reason": "Xで「新年度の職員室」への共感投稿が急拡散中。ダイ先生の「現場の本音語り」スタイルと相性が最高。",
            },
        ],
        "stafy_topics": [
            {
                "title": "保護者対応で失敗した話と、そこから学んだこと",
                "opening": "今日はですね、私が実際にやらかした保護者対応の失敗談をぶっちゃけようと思います。",
                "talk_points": [
                    "新任1年目にやってしまった「絶対NG」な返し方の実体験",
                    "クレームを「チャンス」に変えた転換点の出来事",
                    "今ならこう言う、という具体的な言葉のテンプレート",
                ],
                "closing": "失敗から学んだことって、成功体験より100倍血肉になるんですよね。皆さんもぜひ失敗を怖がらずに。",
                "estimated_minutes": 20,
                "reason": "「保護者対応」コメントが最多。失敗談＋学びの構成はリスナーの信頼を一気に上げる。",
            },
            {
                "title": "教員を辞めたいと思ったあの夜の話",
                "opening": "今日はですね、ちょっと重い話をしようと思います。私が本気で辞めようと思った夜のことです。",
                "talk_points": [
                    "何がそこまで追い詰めたのか（具体的な状況を正直に話す）",
                    "踏みとどまった理由と、そのときの子どもの言葉",
                    "今の自分が「あの夜の自分」に伝えたいこと",
                ],
                "closing": "今しんどい先生に届いてほしい。あなたのしんどさは本物で、あなたの頑張りも本物です。",
                "estimated_minutes": 25,
                "reason": "「教員を辞めたいと思ったとき」投稿が高エンゲージメント。スタエフの温度感と完全合致するテーマ。",
            },
        ],
        "youtube_live_topics": [
            {
                "title": "【4月緊急企画】学級開き完全攻略＆視聴者お悩み相談ライブ",
                "description": "新年度の学級開きで失敗しないための実践的な方法を徹底解説。後半は視聴者のリアルな悩みにライブで答えます。",
                "agenda": [
                    "（0〜10分）自己紹介＋新年度の近況報告・視聴者コメント確認",
                    "（10〜30分）学級開きで最初の1週間にやること・やらないこと",
                    "（30〜45分）保護者・管理職・同僚との関係構築の初動戦略",
                    "（45〜60分）視聴者からのリアルタイムお悩み相談タイム",
                ],
                "q_and_a_seeds": [
                    "特別支援が必要な子が複数いる学級、最初のアプローチは？",
                    "前任の担任と比べられたときの対処法を教えてください",
                    "管理職と相性が悪いとき、どう乗り越えましたか？",
                ],
                "recommended_duration_min": 60,
                "reason": "4月の新年度＋ニュースの「教員不足」「学級開き」が重なる最高のタイミング。ライブは新規フォロワー獲得の最強施策。",
            },
        ],
    }

    kpi = {
        "followers_count": account.get("followers_count", 0),
        "media_count": account.get("media_count", 0),
        "avg_likes": df["like_count"].mean() if not df.empty else 0,
        "avg_comments": df["comments_count"].mean() if not df.empty else 0,
    }

    hot_comments = get_mock_hot_comments()
    past_posts = get_mock_past_posts()

    return generate_html_report(
        report=mock_ai_report,
        account_name=account.get("name", "ダイ先生"),
        kpi=kpi,
        news_items=scored_news_sorted,
        top3_ideas=top3,
        dual_summary=dual,
        hot_comments=hot_comments,
        past_posts=past_posts,
    )


def _get_cached_html() -> str:
    """TTLキャッシュ付きでレポートHTMLを返す（10分間再利用）"""
    with _CACHE_LOCK:
        now = time.time()
        if _CACHE["html"] is None or now - _CACHE["ts"] > _CACHE_TTL:
            _CACHE["html"] = _build_report_html()
            _CACHE["ts"] = now
        return _CACHE["html"]


@app.route("/")
def index():
    return _get_cached_html()


@app.route("/refresh")
def refresh():
    with _CACHE_LOCK:
        _CACHE["html"] = None  # キャッシュ強制クリア
    return redirect(url_for("index"))


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  ダイ先生 コンテンツ分析ダッシュボード")
    print("  → http://localhost:8080")
    print("  Ctrl+C で停止")
    print("=" * 50 + "\n")
    app.run(host="0.0.0.0", port=8080, debug=False)
