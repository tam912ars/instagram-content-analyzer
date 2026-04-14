"""モックデータでHTMLレポートをプレビュー生成するスクリプト"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from src.visualization.html_report import generate_html_report
from src.trends.mock_news import get_mock_news
from src.trends.scorer import get_top3_content_ideas, get_dual_summary, score_news_item

# モックのレポートデータ（AIなしでレイアウト確認用）
mock_report = {
    "date": "2026年04月12日",
    "summary": "「継続できない」「モチベーション」に関するコメントが急増しており、精神面のコンテンツへの需要が高まっています。",
    "insights": [
        "リールのエンゲージメントがフィードの2.3倍。リール強化が最優先。",
        "「継続」「習慣」キーワードへの反応が特に高い傾向。",
        "「スタエフで聞きました」コメントが増加。クロスメディア効果が出ている。",
    ],
    "feed_ideas": [
        {
            "title": "「やる気がなくてもできる」筋トレ習慣の作り方",
            "hook": "モチベーションに頼るのをやめた日から、筋トレが楽しくなった。",
            "body_points": [
                "やる気ゼロでも動ける「2分ルール」を紹介",
                "環境設計で行動を自動化する方法",
                "続けやすいトレーニング種目の選び方",
            ],
            "caption_template": "【やる気ゼロでも続く筋トレ習慣】\n\nモチベーションに頼るから続かない。\n\n大切なのは「やる気がなくても動ける仕組み」を作ること。\n\n今日から試せる3つのメソッドをまとめました👇\n\n#筋トレ #習慣化 #ダイエット #モチベーション #継続",
            "hashtags": ["#筋トレ", "#習慣化", "#ダイエット", "#モチベーション", "#継続"],
            "reason": "「継続できない」「モチベーション」に関するコメントが過去30日で最多。直接的な解決策を提示するとエンゲージメントが高まる。",
        },
        {
            "title": "食事制限なしで体脂肪を落とす3つの戦略",
            "hook": "カロリー制限より先にやるべきことがある。",
            "body_points": [
                "食事の「タイミング」を整えるだけで変わる理由",
                "筋肉量を維持しながら脂肪だけを落とす食事法",
                "外食でも実践できる簡単なルール",
            ],
            "caption_template": "【食事制限しなくていい理由】\n\n我慢する前に、まず「食べ方」を変えよう。\n\n体脂肪を効率よく落とす3つの戦略👇\n\n#ダイエット #食事管理 #筋トレ飯 #ボディメイク #健康",
            "hashtags": ["#ダイエット", "#食事管理", "#筋トレ飯", "#ボディメイク"],
            "reason": "「食事」「炭水化物」に関するコメントが多く、正しい知識を求めている層が多い。",
        },
    ],
    "reel_ideas": [
        {
            "title": "筋トレ初心者が最初の1週間にやるべきこと",
            "hook_text": "これだけやれば最初の壁は超えられる",
            "structure": [
                "冒頭：「ジムに行ったけど何をすればいい？」という悩みを提示",
                "解説：ビッグ3（スクワット・ベンチ・デッドリフト）の重要性を30秒で説明",
                "実演：正しいフォームのポイントを3つ実演",
                "まとめ：「まず1週間これだけやれOK」とシンプルに締め",
            ],
            "bgm_mood": "アップテンポ・モチベーション系（BPM 120〜140）",
            "reason": "初心者向けコンテンツはシェアされやすく、フォロワー獲得に効果的。「何から始めればいい？」という質問が多い。",
        },
        {
            "title": "Before/After：3ヶ月で変わる体の変化",
            "hook_text": "たった3ヶ月でここまで変わる",
            "structure": [
                "冒頭：ビフォー写真 or 弱い自分のナレーション",
                "変化のプロセスを早送りで紹介（週1の記録）",
                "アフター：数値の変化を図解で表示",
                "行動を促すCTA：「プロフィールのリンクから詳細を確認」",
            ],
            "bgm_mood": "感動系・ドラマチックなBGM（徐々に盛り上がる系）",
            "reason": "変化のストーリーはリールで最もバズりやすいフォーマット。コメントのUGC化を促せる。",
        },
    ],
    "stafy_topics": [
        {
            "title": "継続できない人へ贈る「仕組み化」の話",
            "opening": "今日はですね、よくいただくコメントの中で一番多い「継続できない」という悩みについて、本音で話していきます。",
            "talk_points": [
                "意志力に頼るのが間違いである理由（科学的根拠）",
                "ダイ先生自身が継続するためにやっている具体的な仕組み",
                "リスナーが明日から使えるアクションプラン3つ",
            ],
            "closing": "結局ね、継続って才能じゃなくて設計なんですよ。環境を整えた人が勝つゲームです。ぜひ今日から一つだけ試してみてください。",
            "estimated_minutes": 15,
            "reason": "最多コメントキーワード「継続」「モチベーション」に直接刺さるテーマ。スタエフの温度感に合う深掘りトーク。",
        },
        {
            "title": "リスナーの質問に全力回答！お悩み相談回",
            "opening": "今回はですね、Instagramのコメントやスタエフのレターからいただいた質問に全部答えていきます！",
            "talk_points": [
                "「プロテインはいつ飲めばいい？」への回答",
                "「有酸素運動は筋肉を削る？」についての真実",
                "「食欲が抑えられない夜の対処法」を具体的に解説",
            ],
            "closing": "質問してくれた皆さん、ありがとうございました。また次回もどんどん送ってください！",
            "estimated_minutes": 20,
            "reason": "Q&A形式は親密感が上がりリスナーの継続率が高い。コメント内の質問を活用することでコンテンツ制作コストもゼロ。",
        },
    ],
    "youtube_live_topics": [
        {
            "title": "【完全保存版】体脂肪を落として筋肉をつける最速ロードマップ2026",
            "description": "ダイエットと筋トレを同時に成功させるための完全戦略をライブで解説。視聴者のリアルな質問に答えながら、今日から実践できる具体的な方法をお伝えします。",
            "agenda": [
                "（0〜10分）自己紹介＋今日のゴール設定",
                "（10〜30分）筋肉と脂肪の基本原理をわかりやすく解説",
                "（30〜50分）具体的な食事・トレーニングプランを公開",
                "（50〜60分）視聴者からの質問タイム（リアルタイムQ&A）",
            ],
            "q_and_a_seeds": [
                "筋トレと有酸素運動、どちらを先にやるべきですか？",
                "週に何回トレーニングすれば効果が出ますか？",
                "プロテインは必須ですか？食事だけでも大丈夫？",
                "停滞期はどう乗り越えればいいですか？",
            ],
            "recommended_duration_min": 60,
            "reason": "「体脂肪」「筋肉」に関するコメントが最多。包括的なライブは新規フォロワー獲得とエンゲージメント向上に効果的。",
        },
    ],
}

kpi = {
    "followers_count": 12500,
    "media_count": 245,
    "avg_likes": 287,
    "avg_comments": 34,
}

news_items = get_mock_news()
comment_keywords = [("継続", 18), ("筋トレ", 15), ("モチベーション", 12), ("習慣", 10), ("ダイエット", 9)]
captions = []
scored_news = [score_news_item(item, comment_keywords, captions) for item in news_items]
scored_news_sorted = sorted(scored_news, key=lambda x: x.get("trend_score", 0), reverse=True)
top3 = get_top3_content_ideas(news_items, comment_keywords, captions)
dual = get_dual_summary(comment_keywords, news_items)

html = generate_html_report(
    mock_report,
    account_name="ダイ先生",
    kpi=kpi,
    news_items=scored_news_sorted,
    top3_ideas=top3,
    dual_summary=dual,
)

output_path = "reports/preview_report.html"
os.makedirs("reports", exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ プレビュー生成完了: {output_path}")
