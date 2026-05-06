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


def _fmt_num(n: int) -> str:
    """大きな数字を読みやすくフォーマット"""
    if n >= 10000:
        return f"{n / 10000:.1f}万"
    if n >= 1000:
        return f"{n:,}"
    return str(n)


# ─────────────────────────────────────────────────────────────
# ランク別スタイル定義（ライトテーマ）
# ─────────────────────────────────────────────────────────────
_RANK_STYLES = {
    1: {
        "icon": "🥇",
        "badge": "bg-amber-500 text-white",
        "border": "border-amber-400",
        "header_bg": "bg-gradient-to-r from-amber-50 to-orange-50",
        "score_bar": "bg-amber-400",
        "score_text": "text-amber-600",
        "idea_bg": "bg-amber-50",
        "idea_border": "border-amber-200",
        "idea_label": "text-amber-700",
    },
    2: {
        "icon": "🥈",
        "badge": "bg-slate-400 text-white",
        "border": "border-slate-300",
        "header_bg": "bg-gradient-to-r from-slate-50 to-gray-50",
        "score_bar": "bg-slate-400",
        "score_text": "text-slate-500",
        "idea_bg": "bg-slate-50",
        "idea_border": "border-slate-200",
        "idea_label": "text-slate-600",
    },
    3: {
        "icon": "🥉",
        "badge": "bg-orange-500 text-white",
        "border": "border-orange-400",
        "header_bg": "bg-gradient-to-r from-orange-50 to-amber-50",
        "score_bar": "bg-orange-400",
        "score_text": "text-orange-600",
        "idea_bg": "bg-orange-50",
        "idea_border": "border-orange-200",
        "idea_label": "text-orange-700",
    },
    4: {
        "icon": "4️⃣",
        "badge": "bg-violet-600 text-white",
        "border": "border-violet-400",
        "header_bg": "bg-gradient-to-r from-violet-50 to-purple-50",
        "score_bar": "bg-violet-400",
        "score_text": "text-violet-600",
        "idea_bg": "bg-violet-50",
        "idea_border": "border-violet-200",
        "idea_label": "text-violet-700",
    },
    5: {
        "icon": "5️⃣",
        "badge": "bg-sky-600 text-white",
        "border": "border-sky-400",
        "header_bg": "bg-gradient-to-r from-sky-50 to-blue-50",
        "score_bar": "bg-sky-400",
        "score_text": "text-sky-600",
        "idea_bg": "bg-sky-50",
        "idea_border": "border-sky-200",
        "idea_label": "text-sky-700",
    },
}

_EMOTION_CHIP = {
    "怒り": "bg-red-100 text-red-700",
    "不安": "bg-amber-100 text-amber-700",
    "共感": "bg-emerald-100 text-emerald-700",
    "驚き": "bg-purple-100 text-purple-700",
    "悲しみ": "bg-blue-100 text-blue-700",
    "感動": "bg-pink-100 text-pink-700",
    "期待": "bg-sky-100 text-sky-700",
    "落胆": "bg-slate-100 text-slate-600",
    "懐疑": "bg-orange-100 text-orange-700",
    "疲労感": "bg-zinc-100 text-zinc-600",
    "温かさ": "bg-rose-100 text-rose-700",
}

_CAUTION_STYLE = {
    "高": ("bg-red-50 border-red-200 text-red-700", "🔴"),
    "中": ("bg-amber-50 border-amber-200 text-amber-700", "🟡"),
    "低": ("bg-green-50 border-green-200 text-green-700", "🟢"),
}

_FORMAT_ICON = {
    "リール": "🎬",
    "フィード": "📋",
    "スタエフ": "🎙️",
    "YouTubeライブ": "📺",
}


def _connection_dots(score: int) -> str:
    filled = "●" * min(score, 5)
    empty = "○" * (5 - min(score, 5))
    return (
        f'<span class="text-amber-400">{filled}</span>'
        f'<span class="text-slate-300">{empty}</span>'
    )


def _news_card(rank: int, item: dict) -> str:
    title        = _escape(item.get("title", ""))
    url          = item.get("url", "")
    source_name  = _escape(item.get("source_name", ""))
    published_at = _escape(item.get("published_at", ""))
    genre_tags   = item.get("genre_tags", [])
    emotions     = item.get("emotions", [])
    summary      = _escape(item.get("summary", ""))
    angle        = _escape(item.get("angle_memo", ""))
    trend_score  = item.get("trend_score", 0)
    x_rt_count   = item.get("x_rt_count", 0)
    x_like_count = item.get("x_like_count", 0)
    conn_score   = item.get("connection_score", 0)
    caution_lv   = item.get("caution_level", "")
    caution_rsn  = _escape(item.get("caution_reason", ""))
    formats      = item.get("formats", [])

    style = _RANK_STYLES.get(rank, _RANK_STYLES[5])

    # ── ジャンルタグ ──────────────────────────────────────────
    tags_html = "".join(
        f'<span class="rounded-full bg-slate-100 text-slate-600 border border-slate-200 '
        f'px-2.5 py-0.5 text-xs">{_escape(t)}</span>'
        for t in genre_tags
    )

    # ── 感情チップ（強度上位2つ）───────────────────────────────
    top_emotions = sorted(emotions, key=lambda e: e.get("intensity", 0), reverse=True)[:2]
    emotion_chips = "".join(
        f'<span class="rounded-full px-2.5 py-0.5 text-xs font-medium '
        f'{_EMOTION_CHIP.get(e.get("type", ""), "bg-slate-100 text-slate-600")}">'
        f'{_escape(e.get("type", ""))}</span>'
        for e in top_emotions
    )
    if tags_html and emotion_chips:
        sep = '<span class="text-slate-300 text-xs mx-1 self-center">|</span>'
        tags_row = f'<div class="flex flex-wrap gap-1.5 items-center">{tags_html}{sep}{emotion_chips}</div>'
    elif tags_html or emotion_chips:
        tags_row = f'<div class="flex flex-wrap gap-1.5 items-center">{tags_html}{emotion_chips}</div>'
    else:
        tags_row = ""

    # ── リンクボタン ─────────────────────────────────────────
    url_html = (
        f'<a href="{_escape(url)}" target="_blank" rel="noopener" '
        f'class="shrink-0 rounded-lg bg-white border border-slate-200 hover:bg-indigo-50 '
        f'hover:border-indigo-300 px-3 py-1.5 text-xs text-indigo-600 font-medium '
        f'transition-colors whitespace-nowrap shadow-sm">記事を見る →</a>'
    ) if url else ""

    # ── トレンドスコア バー ────────────────────────────────────
    score_section = f"""
    <div>
      <div class="flex items-center justify-between mb-1">
        <span class="text-xs text-slate-400 font-medium">📊 トレンドスコア</span>
        <span class="text-sm font-bold {style["score_text"]}">{trend_score}<span class="text-xs font-normal text-slate-400">/100</span></span>
      </div>
      <div class="h-2.5 bg-slate-100 rounded-full overflow-hidden">
        <div class="{style["score_bar"]} h-2.5 rounded-full" style="width:{trend_score}%"></div>
      </div>
    </div>"""

    # ── エンゲージメント ─────────────────────────────────────
    engagement_section = ""
    if x_rt_count or x_like_count:
        conn_html = (
            f'<div class="flex flex-col gap-0.5">'
            f'<span class="text-xs text-slate-400">📌 相性</span>'
            f'<span class="text-sm">{_connection_dots(conn_score)}</span>'
            f'</div>'
        ) if conn_score else ""
        engagement_section = f"""
    <div class="flex items-center gap-5 flex-wrap">
      <div class="flex flex-col gap-0.5">
        <span class="text-xs text-slate-400">🔁 リポスト</span>
        <span class="text-sm font-semibold text-slate-700">{_fmt_num(x_rt_count)}</span>
      </div>
      <div class="flex flex-col gap-0.5">
        <span class="text-xs text-slate-400">❤️ いいね</span>
        <span class="text-sm font-semibold text-slate-700">{_fmt_num(x_like_count)}</span>
      </div>
      {conn_html}
    </div>"""

    # ── 推奨フォーマット ─────────────────────────────────────
    formats_html = ""
    if formats:
        chips = "".join(
            f'<span class="rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100 '
            f'px-2.5 py-0.5 text-xs">{_FORMAT_ICON.get(f, "•")} {_escape(f)}</span>'
            for f in formats
        )
        formats_html = f'<div class="flex flex-wrap gap-1.5">{chips}</div>'

    # ── 投稿アイデア ─────────────────────────────────────────
    idea_html = ""
    if angle:
        idea_html = f"""
    <div class="rounded-xl {style["idea_bg"]} border {style["idea_border"]} px-4 py-3">
      <p class="text-xs font-semibold {style["idea_label"]} mb-1.5">📱 投稿アイデア</p>
      <p class="text-sm text-slate-600 leading-relaxed whitespace-pre-wrap">{angle}</p>
    </div>"""

    # ── 注意レベル ────────────────────────────────────────────
    caution_html = ""
    if caution_lv:
        c_style, c_icon = _CAUTION_STYLE.get(caution_lv, ("bg-slate-50 border-slate-200 text-slate-600", "⚠️"))
        caution_html = f"""
    <div class="rounded-xl border {c_style} px-4 py-2.5 flex items-start gap-2 flex-wrap">
      <span class="text-xs font-bold shrink-0">{c_icon} 注意レベル: {_escape(caution_lv)}</span>
      {f'<span class="text-xs opacity-75">{caution_rsn}</span>' if caution_rsn else ""}
    </div>"""

    return f"""
<article class="bg-white rounded-2xl shadow-sm border border-slate-200 border-l-4 {style["border"]} overflow-hidden">

  <!-- カードヘッダー -->
  <div class="{style["header_bg"]} px-5 pt-4 pb-3.5">
    <div class="flex items-start gap-3">
      <!-- ランクバッジ -->
      <div class="flex flex-col items-center gap-1 shrink-0 mt-0.5">
        <span class="text-2xl leading-none">{style["icon"]}</span>
        <span class="rounded-full {style["badge"]} px-2 py-0.5 text-xs font-bold">{rank}位</span>
      </div>
      <!-- タイトル + メタ情報 -->
      <div class="flex-1 min-w-0">
        <h2 class="text-base font-bold text-slate-800 leading-snug mb-1.5">{title}</h2>
        <div class="flex items-center gap-2 flex-wrap text-xs text-slate-500">
          {f'<span class="font-medium text-slate-600">{source_name}</span>' if source_name else ""}
          {f'<span class="text-slate-300">·</span><span>{published_at}</span>' if published_at else ""}
        </div>
      </div>
      {url_html}
    </div>
  </div>

  <!-- カードボディ -->
  <div class="px-5 py-4 space-y-3.5">

    <!-- タグ + 感情 -->
    {tags_row}

    <!-- 概要 -->
    {f'<p class="text-sm text-slate-600 leading-relaxed">{summary}</p>' if summary else ""}

    <!-- スコア + エンゲージメント -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {score_section}
      {engagement_section}
    </div>

    <!-- 推奨フォーマット -->
    {formats_html}

    <!-- 投稿アイデア -->
    {idea_html}

    <!-- 注意レベル -->
    {caution_html}

  </div>
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

    report_date  = _escape(today.strftime("%Y年%m月%d日"))
    weekday      = ["月", "火", "水", "木", "金", "土", "日"][today.weekday()]
    generated_at = datetime.now().strftime("%Y/%m/%d %H:%M")

    top5        = news_items[:5]
    news_html   = "".join(_news_card(i + 1, item) for i, item in enumerate(top5))
    total_count = len(news_items)

    # インデックス（タイトル一覧）
    index_items = "".join(
        f'<li class="flex items-center gap-3 py-2.5 border-b border-slate-100 last:border-0">'
        f'<span class="shrink-0 text-lg">{_RANK_STYLES.get(i + 1, _RANK_STYLES[5])["icon"]}</span>'
        f'<span class="text-sm text-slate-700 leading-snug">{_escape(item.get("title", ""))}</span>'
        f'</li>'
        for i, item in enumerate(top5)
    )

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{_escape(account_name)} 今日の注目ニュース — {report_date}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ["'Noto Sans JP'", 'sans-serif'],
          }},
        }},
      }},
    }}
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet" />
</head>
<body class="min-h-screen bg-slate-100 text-slate-800 font-sans">

<!-- ── Sticky header ── -->
<header class="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-slate-200 shadow-sm">
  <div class="mx-auto max-w-3xl px-4 py-3 flex items-center gap-3">
    <div class="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-700 via-violet-700 to-purple-700 text-white font-black text-sm shrink-0">D</div>
    <div class="flex-1 min-w-0">
      <span class="font-bold text-slate-800 text-sm">{_escape(account_name)}</span>
      <span class="text-slate-400 text-xs ml-2">教師向けニュースレポート</span>
    </div>
    <span class="text-xs text-slate-500 shrink-0 hidden sm:block">{report_date}（{weekday}）</span>
  </div>
</header>

<!-- ── ヒーローヘッダー ── -->
<div class="bg-gradient-to-br from-indigo-700 via-violet-700 to-purple-700 text-white">
  <div class="mx-auto max-w-3xl px-6 py-10">
    <p class="text-indigo-200 text-xs font-semibold tracking-widest uppercase mb-3">Daily Education News</p>
    <h1 class="text-3xl sm:text-4xl font-black mb-2 leading-tight">
      {report_date}（{weekday}）
    </h1>
    <p class="text-indigo-200 text-sm">
      教師向けニュース <span class="text-white font-bold">{total_count}件</span> を収集 ·
      注目度の高い <span class="text-amber-300 font-bold">Top 5</span> をピックアップ
    </p>
  </div>
</div>

<main class="mx-auto max-w-3xl px-4 py-8 space-y-8">

  <!-- ── 目次 ── -->
  <section class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
    <div class="px-5 pt-4 pb-2 flex items-center gap-2 border-b border-slate-100">
      <span class="text-lg">📰</span>
      <h2 class="text-sm font-bold text-slate-700">今日のTop 5 一覧</h2>
    </div>
    <ul class="px-5 pb-2">
      {index_items}
    </ul>
  </section>

  <!-- ── セクションタイトル ── -->
  <div class="flex items-center gap-3">
    <div>
      <h2 class="text-lg font-bold text-slate-800">詳細レポート</h2>
      <div class="mt-1 w-16 h-[3px] rounded bg-gradient-to-r from-amber-400 via-pink-400 to-indigo-400"></div>
    </div>
    <span class="ml-auto text-xs text-slate-400">生成: {generated_at}</span>
  </div>

  <!-- ── Top 5 ニュースカード ── -->
  <div class="space-y-5">
    {news_html}
  </div>

  <!-- ── 注記 ── -->
  <div class="rounded-xl border border-slate-200 bg-white px-4 py-3 text-xs text-slate-400 text-center shadow-sm">
    📌 投稿アイデアは AI による提案です。実際の発信時は内容をご確認ください。
  </div>

</main>

<footer class="mt-8 border-t border-slate-200 bg-white py-6">
  <div class="mx-auto max-w-3xl px-4 flex items-center justify-between flex-wrap gap-2">
    <p class="text-xs text-slate-400">{_escape(account_name)} コンテンツ分析ツール</p>
    <p class="text-xs text-slate-400">生成日時: {generated_at}</p>
  </div>
</footer>

</body>
</html>"""
