"""シングルページ HTML レポート生成モジュール（今日の注目ニュース Top5）"""
from datetime import date, datetime


def _escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


# ─────────────────────────────────────────────────────────────
# ランクバッジの色設定
# ─────────────────────────────────────────────────────────────
_RANK_STYLES = {
    1: {
        "badge": "bg-amber-500 text-white",
        "border": "border-amber-500/40",
        "bg": "from-amber-950/40 to-slate-900",
        "accent": "border-amber-400",
        "label": "text-amber-300",
        "icon": "🥇",
    },
    2: {
        "badge": "bg-slate-400 text-white",
        "border": "border-slate-500/40",
        "bg": "from-slate-800/60 to-slate-900",
        "accent": "border-slate-400",
        "label": "text-slate-300",
        "icon": "🥈",
    },
    3: {
        "badge": "bg-orange-600 text-white",
        "border": "border-orange-600/40",
        "bg": "from-orange-950/40 to-slate-900",
        "accent": "border-orange-400",
        "label": "text-orange-300",
        "icon": "🥉",
    },
    4: {
        "badge": "bg-violet-700 text-white",
        "border": "border-violet-600/40",
        "bg": "from-violet-950/40 to-slate-900",
        "accent": "border-violet-400",
        "label": "text-violet-300",
        "icon": "4️⃣",
    },
    5: {
        "badge": "bg-sky-700 text-white",
        "border": "border-sky-600/40",
        "bg": "from-sky-950/40 to-slate-900",
        "accent": "border-sky-400",
        "label": "text-sky-300",
        "icon": "5️⃣",
    },
}

_EMOTION_CHIP = {
    "怒り": "bg-red-900/70 text-red-300",
    "不安": "bg-amber-900/70 text-amber-300",
    "共感": "bg-emerald-900/70 text-emerald-300",
    "驚き": "bg-purple-900/70 text-purple-300",
    "悲しみ": "bg-blue-900/70 text-blue-300",
    "感動": "bg-pink-900/70 text-pink-300",
    "期待": "bg-sky-900/70 text-sky-300",
    "落胆": "bg-slate-700 text-slate-400",
    "懐疑": "bg-orange-900/70 text-orange-300",
    "疲労感": "bg-zinc-700 text-zinc-300",
    "温かさ": "bg-rose-900/70 text-rose-300",
}


def _news_card(rank: int, item: dict) -> str:
    title = _escape(item.get("title", ""))
    url = item.get("url", "")
    source_name = _escape(item.get("source_name", ""))
    published_at = _escape(item.get("published_at", ""))
    genre_tags = item.get("genre_tags", [])
    emotions = item.get("emotions", [])
    summary = _escape(item.get("summary", ""))
    angle = _escape(item.get("angle_memo", ""))

    style = _RANK_STYLES.get(rank, _RANK_STYLES[5])

    # ジャンルタグ
    tags_html = "".join(
        f'<span class="rounded-full bg-slate-700/70 px-2.5 py-0.5 text-xs text-slate-300">{_escape(t)}</span>'
        for t in genre_tags
    )

    # 感情チップ（強い順 上位2つ）
    sorted_emotions = sorted(emotions, key=lambda e: e.get("intensity", 0), reverse=True)[:2]
    emotion_chips = "".join(
        f'<span class="rounded-full px-2.5 py-0.5 text-xs font-medium {_EMOTION_CHIP.get(e.get("type", ""), "bg-slate-700 text-slate-300")}">{_escape(e.get("type", ""))}</span>'
        for e in sorted_emotions
    )

    url_html = (
        f'<a href="{_escape(url)}" target="_blank" rel="noopener" '
        f'class="shrink-0 rounded-lg bg-slate-700/60 hover:bg-slate-600/60 px-3 py-1.5 text-xs text-blue-400 transition-colors font-medium">🔗 記事を開く</a>'
    ) if url else ""

    post_section = ""
    if angle:
        post_section = f"""
  <!-- X / Threads 投稿案 -->
  <div class="rounded-xl bg-slate-800/80 border-l-2 {style["accent"]} px-4 py-3">
    <p class="text-xs font-semibold {style["label"]} mb-2">📱 X / Threads 投稿案</p>
    <p class="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">{angle}</p>
  </div>"""

    return f"""
<article class="rounded-2xl border {style["border"]} bg-gradient-to-br {style["bg"]} p-5 flex flex-col gap-4">

  <!-- ヘッダー：ランク + 出典 + リンク -->
  <div class="flex items-center gap-3 flex-wrap">
    <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full {style["badge"]} text-sm font-black">{rank}</span>
    <span class="text-lg shrink-0">{style["icon"]}</span>
    <span class="text-xs text-slate-400 flex-1 truncate">{source_name}</span>
    {f'<span class="text-xs text-slate-500 shrink-0">{published_at}</span>' if published_at else ""}
    {url_html}
  </div>

  <!-- タイトル -->
  <h2 class="text-lg font-bold text-slate-50 leading-snug">{title}</h2>

  <!-- ジャンル + 感情 -->
  <div class="flex flex-wrap gap-1.5 items-center">
    {tags_html}
    {f'<span class="text-slate-600 text-xs mx-0.5">·</span>{emotion_chips}' if emotion_chips else ""}
  </div>

  <!-- 概要 -->
  {f'<p class="text-sm text-slate-400 leading-relaxed">{summary}</p>' if summary else ""}

  {post_section}

</article>"""


# ─────────────────────────────────────────────────────────────
# メイン生成関数
# ─────────────────────────────────────────────────────────────

def generate_html_report(
    news_items: list,
    account_name: str = "ダイ先生",
    today: date = None,
) -> str:
    if today is None:
        today = date.today()

    report_date = _escape(today.strftime("%Y年%m月%d日"))
    weekday = ["月", "火", "水", "木", "金", "土", "日"][today.weekday()]
    generated_at = datetime.now().strftime("%Y/%m/%d %H:%M")

    top5 = news_items[:5]
    news_html = "".join(_news_card(i + 1, item) for i, item in enumerate(top5))
    total_count = len(news_items)

    return f"""<!DOCTYPE html>
<html lang="ja" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{_escape(account_name)} 今日の注目ニュース — {report_date}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>tailwind.config = {{ darkMode: 'class' }}</script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet" />
  <style>
    body {{ font-family: 'Noto Sans JP', sans-serif; }}
    .gradient-text {{
      background: linear-gradient(135deg, #c084fc 0%, #f472b6 50%, #60a5fa 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }}
  </style>
</head>
<body class="min-h-screen bg-[#0a0f1e] text-slate-100">

<!-- ── Sticky header ── -->
<header class="sticky top-0 z-50 border-b border-slate-800 bg-[#0d1424]/95 backdrop-blur-sm">
  <div class="mx-auto max-w-4xl px-4 py-3 flex items-center gap-3">
    <div class="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-pink-600 text-white font-black text-sm shrink-0">D</div>
    <div class="flex-1 min-w-0">
      <span class="font-bold text-slate-200 text-sm">{_escape(account_name)}</span>
      <span class="text-slate-500 text-xs ml-2">今日の注目ニュース</span>
    </div>
    <span class="text-xs text-slate-500 shrink-0">{report_date}（{weekday}）</span>
  </div>
</header>

<main class="mx-auto max-w-4xl px-4 py-10 space-y-10">

  <!-- ── ヒーローセクション ── -->
  <section class="text-center space-y-4">
    <p class="text-xs font-semibold tracking-widest uppercase text-slate-500">Daily Education News</p>
    <h1 class="text-4xl font-black gradient-text">{report_date}（{weekday}）</h1>
    <p class="text-sm text-slate-500">
      教師向けニュース <span class="font-bold text-slate-300">{total_count}件</span> を収集 ·
      注目度の高い <span class="font-bold text-amber-300">Top 5</span> をピックアップ
    </p>
  </section>

  <!-- ── Top 5 ニュース ── -->
  <section class="space-y-5">
    <div class="flex items-center gap-3">
      <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-600/20 border border-amber-500/40 text-lg shrink-0">📰</div>
      <div>
        <p class="text-xs font-semibold uppercase tracking-wider text-amber-400">Today's Top 5</p>
        <h2 class="text-lg font-bold text-amber-200">今日の注目ニュース</h2>
      </div>
      <span class="ml-auto rounded-full bg-amber-900/40 border border-amber-700/40 px-3 py-1 text-xs text-amber-300 font-medium">Top 5</span>
    </div>

    <div class="space-y-5">
      {news_html}
    </div>
  </section>

  <!-- ── 注記 ── -->
  <div class="rounded-xl border border-slate-800 bg-slate-900/60 px-4 py-3 text-xs text-slate-500 text-center">
    📌 X / Threads 投稿案は今後、詳細なフォーマット指示に基づき更新予定です
  </div>

</main>

<footer class="mt-12 border-t border-slate-800 bg-[#0d1424]/80 py-5">
  <div class="mx-auto max-w-4xl px-4 flex items-center justify-between flex-wrap gap-2">
    <p class="text-xs text-slate-600">{_escape(account_name)} コンテンツ分析ツール</p>
    <p class="text-xs text-slate-600">生成日時: {generated_at}</p>
  </div>
</footer>

</body>
</html>"""
