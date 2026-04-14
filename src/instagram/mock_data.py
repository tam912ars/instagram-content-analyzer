"""開発・デモ用のモックデータ（APIキーなしでも動作確認できる）"""
from datetime import datetime, timedelta
import random


def generate_mock_posts(count: int = 20) -> list[dict]:
    topics = [
        ("学級開きで絶対やってはいけないこと3選", "IMAGE"),
        ("新年度の職員室、先生の本音", "CAROUSEL_ALBUM"),
        ("保護者からのクレーム、どう対応する？", "IMAGE"),
        ("部活指導ゼロでも評価された理由", "VIDEO"),
        ("教員の残業を減らした「3つの習慣」", "IMAGE"),
        ("子どもが心を開く声かけのコツ", "VIDEO"),
        ("学校では教えてくれない「学級経営の本質」", "IMAGE"),
        ("不登校の子への最初の一歩", "IMAGE"),
        ("先生が病む前に知っておきたいこと", "VIDEO"),
        ("保護者対応で失敗しないための思考法", "IMAGE"),
        ("授業が劇的に変わる板書のコツ", "VIDEO"),
        ("若手教員が最初に覚えるべき学校のルール", "IMAGE"),
        ("教員採用試験に受かる人の共通点", "IMAGE"),
        ("先生あるある：職員室の人間関係リアル", "VIDEO"),
        ("子どものやる気を引き出す「問いかけ」の技術", "IMAGE"),
        ("放課後の時間を奪われないために", "IMAGE"),
        ("特別支援が必要な子への正しいアプローチ", "VIDEO"),
        ("PTAとうまくやる方法", "IMAGE"),
        ("教員を辞めたいと思ったとき読んでほしい話", "VIDEO"),
        ("担任として大切にしてきた「たった一つのこと」", "IMAGE"),
    ]

    comment_templates = [
        "めちゃくちゃ参考になりました！",
        "新任1年目でこれ知りたかったです",
        "ダイ先生のおかげで学級経営が変わりました",
        "{}についてもっと詳しく教えてください",
        "スタエフで深堀りしてほしいです！",
        "YouTubeライブで質問したいです",
        "保護者対応で悩んでいたのでとても助かりました",
        "職員室でこそっとシェアしました",
        "友達の先生にも送りました",
        "うちの管理職に見せたい…",
        "これ、教員採用試験の面接でも使えますか？",
        "学校の現実をここまで言語化してくれる人いなかった",
        "先生が一番しんどいの、わかってほしい",
        "毎朝見てモチベ上げてます！",
        "もっと早く出会いたかったです",
        "この考え方、目から鱗でした",
        "{}ってどうすればいいですか？",
        "ずっと悩んでたのが解決しました",
    ]

    question_variants = ["保護者対応", "特別支援", "不登校対応", "部活の断り方", "管理職との関係"]

    posts = []
    now = datetime.now()

    for i, (caption, media_type) in enumerate(topics[:count]):
        days_ago = i * 3 + random.randint(0, 2)
        post_date = now - timedelta(days=days_ago)
        likes = random.randint(80, 1200)
        comment_count = random.randint(8, 80)

        comments = []
        for j in range(min(comment_count, 15)):
            template = random.choice(comment_templates)
            if "{}" in template:
                template = template.format(random.choice(question_variants))
            comments.append({
                "id": f"comment_{i}_{j}",
                "text": template,
                "timestamp": (post_date + timedelta(hours=random.randint(1, 72))).isoformat(),
                "like_count": random.randint(0, 50),
                "username": f"teacher_{random.randint(1000, 9999)}",
            })

        posts.append({
            "id": f"post_{i}",
            "caption": f"【{caption}】\n\n現場の先生に伝えたいことをまとめました。\n\n#教員 #先生 #学級経営 #教育 #新年度 #教師の働き方",
            "media_type": media_type,
            "timestamp": post_date.isoformat(),
            "like_count": likes,
            "comments_count": comment_count,
            "comments": comments,
        })

    return posts


def generate_mock_account() -> dict:
    return {
        "id": "dy.papa_teacher",
        "name": "ダイ先生",
        "username": "dy.papa_teacher",
        "followers_count": 18400,
        "follows_count": 210,
        "media_count": 312,
        "biography": "現役教員パパ｜学校・教育・先生の働き方を発信｜スタエフ・YouTubeライブ毎週開催",
    }
