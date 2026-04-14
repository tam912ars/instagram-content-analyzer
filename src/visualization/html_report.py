"""Tailwind CSS + JavaScript タブ構成 HTML レポート生成モジュール"""
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


def _score_bar(score: int, color: str = "bg-violet-500") -> str:
    pct = min(max(score, 0), 100)
    return f"""<div class="flex items-center gap-2">
      <div class="flex-1 h-1.5 rounded-full bg-slate-700">
        <div class="{color} h-1.5 rounded-full" style="width:{pct}%"></div>
      </div>
      <span class="text-xs text-slate-400 w-7 text-right shrink-0">{pct}</span>
    </div>"""


# ─────────────────────────────────────────────────────────────
# PAGE 1: ダッシュボード
# ─────────────────────────────────────────────────────────────

def _dual_summary(dual: dict) -> str:
    follower_topics = dual.get("follower_topics", [])
    external_topics = dual.get("external_topics", [])
    dominant_emotion = _escape(dual.get("dominant_emotion", ""))
    seasonal_kw = dual.get("seasonal_keywords", [])
    top_news_title = _escape(dual.get("top_news_title", ""))
    top_news_score = dual.get("top_news_score", 0)

    follower_pills = "".join(
        f'<span class="rounded-full bg-violet-900/70 border border-violet-700/50 px-3 py-1 text-sm text-violet-200 font-medium">{_escape(t)}</span>'
        for t in follower_topics
    )
    external_items = "".join(
        f'<li class="flex items-start gap-2 text-sm text-slate-300"><span class="text-orange-400 shrink-0">▸</span><span>{_escape(t)}</span></li>'
        for t in external_topics
    )
    seasonal_pills = "".join(
        f'<span class="rounded-full bg-emerald-900/50 border border-emerald-700/40 px-2 py-0.5 text-xs text-emerald-300">{_escape(kw)}</span>'
        for kw in seasonal_kw
    )

    return f"""
<div class="rounded-2xl border border-slate-700/50 bg-gradient-to-r from-slate-800/60 to-slate-900/60 p-6 grid md:grid-cols-2 gap-6 mb-8">
  <div>
    <div class="flex items-center gap-2 mb-3">
      <span class="text-lg">📊</span>
      <h2 class="text-sm font-bold uppercase tracking-wider text-violet-400">今フォロワーが反応していること</h2>
    </div>
    <div class="flex flex-wrap gap-2 mb-4">{follower_pills}</div>
    <div class="flex flex-wrap gap-1 items-center">
      <span class="text-xs text-slate-500 mr-1">🗓️ 旬：</span>{seasonal_pills}
    </div>
  </div>
  <div class="border-t md:border-t-0 md:border-l border-slate-700/50 pt-4 md:pt-0 md:pl-6">
    <div class="flex items-center gap-2 mb-3">
      <span class="text-lg">📰</span>
      <h2 class="text-sm font-bold uppercase tracking-wider text-orange-400">今外部で話題の教育テーマ</h2>
    </div>
    <ul class="space-y-2 mb-4">{external_items}</ul>
    <div class="rounded-xl bg-orange-900/30 border border-orange-700/40 px-3 py-2 flex items-center gap-2">
      <span class="text-xs text-orange-400 shrink-0">🔥 最注目：</span>
      <span class="text-xs text-orange-200 font-medium leading-snug flex-1">{top_news_title}</span>
      <span class="text-xs font-bold text-orange-300 shrink-0">{top_news_score}pt</span>
    </div>
    {f'<p class="mt-2 text-xs text-slate-500">主な感情傾向：<span class="text-slate-300 font-medium">{dominant_emotion}</span></p>' if dominant_emotion else ""}
  </div>
</div>"""


def _top3_card(rank: int, item: dict) -> str:
    title = _escape(item.get("title", ""))
    angle = _escape(item.get("angle_memo", ""))
    formats = item.get("formats", [])
    genre_tags = item.get("genre_tags", [])

    medals = {
        1: ("🥇", "from-amber-900/60 to-yellow-900/40 border-amber-500/50", "bg-amber-500", "text-amber-300"),
        2: ("🥈", "from-slate-700/60 to-slate-800/50 border-slate-500/50", "bg-slate-400", "text-slate-300"),
        3: ("🥉", "from-orange-900/50 to-amber-900/30 border-orange-600/50", "bg-orange-600", "text-orange-300"),
    }
    medal, card_cls, badge_cls, rank_text_cls = medals.get(rank, medals[3])

    _FORMAT_BADGE = {
        "リール": "bg-pink-900/70 text-pink-200 border border-pink-700/40",
        "フィード": "bg-violet-900/70 text-violet-200 border border-violet-700/40",
        "YouTubeライブ": "bg-red-900/70 text-red-200 border border-red-700/40",
        "スタエフ": "bg-sky-900/70 text-sky-200 border border-sky-700/40",
        "Instagram": "bg-violet-900/70 text-violet-200 border border-violet-700/40",
    }
    fmts = "".join(
        f'<span class="rounded-full px-2.5 py-0.5 text-xs font-medium {_FORMAT_BADGE.get(f, "bg-slate-700 text-slate-300 border border-slate-600")}">{_escape(f)}</span>'
        for f in formats
    )
    tags = "".join(
        f'<span class="rounded-full bg-slate-700/60 px-2 py-0.5 text-xs text-slate-400">{_escape(t)}</span>'
        for t in genre_tags
    )

    return f"""
<div class="rounded-2xl border bg-gradient-to-br {card_cls} p-5 flex flex-col gap-4 relative">
  <!-- ランクバッジ -->
  <div class="flex items-center gap-2">
    <span class="flex h-7 w-7 items-center justify-center rounded-full {badge_cls} text-white text-xs font-black shrink-0">{rank}</span>
    <span class="{rank_text_cls} text-xs font-semibold tracking-widest">Rank {rank}</span>
    <span class="ml-auto text-2xl">{medal}</span>
  </div>

  <!-- タイトル（大きく・くっきり） -->
  <h3 class="text-base font-bold text-white leading-snug">{title}</h3>

  <!-- ジャンルタグ -->
  <div class="flex flex-wrap gap-1">{tags}</div>

  <!-- 向いている形式 -->
  <div class="flex flex-wrap gap-1">{fmts}</div>

  <!-- 切り口メモ -->
  <div class="rounded-xl bg-black/25 border-l-2 border-white/30 px-3 py-2.5">
    <p class="text-xs font-semibold text-slate-400 mb-1">✏️ 推奨切り口</p>
    <p class="text-xs text-slate-200 leading-relaxed">{angle}</p>
  </div>
</div>"""


def _instagram_card(idx: int, idea: dict) -> str:
    title = _escape(idea.get("title", ""))
    hook = _escape(idea.get("hook", ""))
    caption = _escape(idea.get("caption_template", ""))
    reason = _escape(idea.get("reason", ""))
    points = idea.get("body_points", [])
    tags = idea.get("hashtags", [])
    fmt = _escape(idea.get("format_suggestion", ""))
    fmt_reason = _escape(idea.get("format_reason", ""))

    fmt_color = "bg-pink-700" if "リール" in fmt else "bg-violet-700" if "フィード" in fmt else "bg-indigo-700"
    points_html = "".join(
        f'<li class="flex items-start gap-2"><span class="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-violet-400"></span><span>{_escape(p)}</span></li>'
        for p in points
    )
    tags_html = "".join(
        f'<span class="rounded-full bg-violet-900/60 px-2 py-0.5 text-xs text-violet-300">{_escape(t)}</span>'
        for t in tags
    )

    return f"""
<div class="rounded-2xl border border-violet-500/40 bg-gradient-to-br from-[#1a1032] to-[#1e1540] p-5">
  <div class="mb-3 flex items-start justify-between gap-2">
    <div class="flex items-center gap-2 flex-1 min-w-0">
      <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-violet-600 text-xs font-bold text-white">{idx}</span>
      <h3 class="text-sm font-bold text-violet-200 leading-snug">{title}</h3>
    </div>
    {f'<span class="shrink-0 rounded-full {fmt_color} px-2 py-0.5 text-xs text-white font-medium">{fmt}</span>' if fmt else ""}
  </div>
  {f'<p class="mb-3 text-xs text-slate-500 pl-8">📋 {fmt_reason}</p>' if fmt_reason else ""}
  <div class="mb-3 rounded-xl bg-violet-950/60 px-4 py-3 border-l-2 border-violet-400">
    <p class="text-xs font-semibold text-violet-400 mb-1">🎣 フック</p>
    <p class="text-sm text-violet-100 italic">「{hook}」</p>
  </div>
  <div class="mb-3">
    <p class="mb-2 text-xs font-semibold text-violet-400">📝 本文ポイント</p>
    <ul class="space-y-1 text-sm text-slate-300">{points_html}</ul>
  </div>
  <div class="mb-3 rounded-xl bg-slate-800/60 p-3">
    <p class="mb-1 text-xs font-semibold text-violet-400">✍️ キャプションテンプレート</p>
    <p class="whitespace-pre-wrap text-xs text-slate-400 font-mono leading-relaxed">{caption}</p>
  </div>
  <div class="mb-3 flex flex-wrap gap-1">{tags_html}</div>
  <p class="text-xs text-slate-500">💬 {reason}</p>
</div>"""


def _stafy_card(idx: int, t: dict) -> str:
    title = _escape(t.get("title", ""))
    opening = _escape(t.get("opening", ""))
    closing = _escape(t.get("closing", ""))
    minutes = t.get("estimated_minutes", 15)
    reason = _escape(t.get("reason", ""))
    points_html = "".join(
        f'<li class="flex items-start gap-2"><span class="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-sky-400"></span><span>{_escape(p)}</span></li>'
        for p in t.get("talk_points", [])
    )
    return f"""
<div class="rounded-2xl border border-sky-500/40 bg-gradient-to-br from-[#07172a] to-[#0d1e30] p-5">
  <div class="mb-3 flex items-center justify-between gap-2">
    <div class="flex items-center gap-2">
      <span class="flex h-6 w-6 items-center justify-center rounded-full bg-sky-600 text-xs font-bold text-white">{idx}</span>
      <h3 class="text-sm font-bold text-sky-200">{title}</h3>
    </div>
    <span class="rounded-full bg-sky-900/60 px-2 py-0.5 text-xs text-sky-300 shrink-0">⏱ {minutes}分</span>
  </div>
  <div class="mb-3 rounded-xl bg-sky-950/60 px-4 py-3 border-l-2 border-sky-400">
    <p class="text-xs font-semibold text-sky-400 mb-1">🎤 冒頭トーク</p>
    <p class="text-sm text-sky-100 italic">「{opening}」</p>
  </div>
  <ul class="space-y-1 text-sm text-slate-300 mb-3">{points_html}</ul>
  <div class="mb-3 rounded-xl bg-sky-950/60 px-4 py-3 border-l-2 border-sky-300">
    <p class="text-xs font-semibold text-sky-400 mb-1">🔚 締め</p>
    <p class="text-sm text-sky-100 italic">「{closing}」</p>
  </div>
  <p class="text-xs text-slate-500">💬 {reason}</p>
</div>"""


def _youtube_card(idx: int, t: dict) -> str:
    title = _escape(t.get("title", ""))
    desc = _escape(t.get("description", ""))
    dur = t.get("recommended_duration_min", 60)
    reason = _escape(t.get("reason", ""))
    agenda_html = "".join(
        f'<div class="flex items-start gap-2"><span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-red-700/80 text-xs font-bold text-white">{i}</span><p class="text-sm text-slate-300">{_escape(a)}</p></div>'
        for i, a in enumerate(t.get("agenda", []), 1)
    )
    qa_html = "".join(
        f'<div class="flex items-start gap-2 rounded-lg bg-red-950/40 px-3 py-2"><span class="text-red-400 shrink-0 font-bold text-xs">Q.</span><p class="text-sm text-slate-300">{_escape(q)}</p></div>'
        for q in t.get("q_and_a_seeds", [])
    )
    return f"""
<div class="rounded-2xl border border-red-500/40 bg-gradient-to-br from-[#1f0707] to-[#2a0d0d] p-5">
  <div class="mb-3 flex items-center justify-between gap-2">
    <div class="flex items-center gap-2">
      <span class="flex h-6 w-6 items-center justify-center rounded-full bg-red-600 text-xs font-bold text-white">{idx}</span>
      <h3 class="text-sm font-bold text-red-200">{title}</h3>
    </div>
    <span class="rounded-full bg-red-900/60 px-2 py-0.5 text-xs text-red-300 shrink-0">⏱ {dur}分</span>
  </div>
  <div class="mb-3 rounded-xl bg-red-950/60 px-4 py-3">
    <p class="text-xs font-semibold text-red-400 mb-1">📄 概要</p>
    <p class="text-sm text-red-100">{desc}</p>
  </div>
  <div class="mb-3 space-y-2">{agenda_html}</div>
  <div class="mb-3 space-y-2">{qa_html}</div>
  <p class="text-xs text-slate-500">💬 {reason}</p>
</div>"""


def _insight_pill(text: str) -> str:
    return f'<div class="flex items-start gap-2 rounded-xl bg-slate-800/80 border border-slate-700/60 px-4 py-3"><span class="text-amber-400 shrink-0 mt-0.5">💡</span><p class="text-sm text-slate-300">{_escape(text)}</p></div>'


# ─────────────────────────────────────────────────────────────
# PAGE 2: 外部トレンド・教育ニュース
# ─────────────────────────────────────────────────────────────

_SOURCE_BADGE = {
    "教育新聞": "bg-blue-900/70 text-blue-300 border-blue-700/50",
    "地方新聞": "bg-teal-900/70 text-teal-300 border-teal-700/50",
    "X": "bg-slate-700/70 text-slate-200 border-slate-600/50",
}
_CAUTION_STYLE = {
    "低": ("bg-emerald-900/40 text-emerald-300", "🟢"),
    "中": ("bg-amber-900/40 text-amber-300", "🟡"),
    "高": ("bg-red-900/40 text-red-300", "🔴"),
}
_EMOTION_COLOR = {
    "怒り": "bg-red-700", "不安": "bg-amber-700", "共感": "bg-emerald-700",
    "驚き": "bg-purple-700", "悲しみ": "bg-blue-700", "感動": "bg-pink-700",
    "期待": "bg-sky-700", "落胆": "bg-slate-600", "懐疑": "bg-orange-700",
    "疲労感": "bg-zinc-600", "あきらめ": "bg-zinc-500", "温かさ": "bg-rose-700",
}
_FORMAT_BADGE_NEWS = {
    "リール": "bg-pink-900/70 text-pink-300", "フィード": "bg-violet-900/70 text-violet-300",
    "YouTubeライブ": "bg-red-900/70 text-red-300", "スタエフ": "bg-sky-900/70 text-sky-300",
    "Instagram": "bg-violet-900/70 text-violet-300",
}


def _emotion_bars(emotions: list) -> str:
    return "".join(
        f"""<div class="flex items-center gap-2 text-xs">
          <span class="w-10 text-slate-400 shrink-0">{_escape(e.get("type",""))}</span>
          <div class="flex-1 h-1.5 rounded-full bg-slate-700">
            <div class="{_EMOTION_COLOR.get(e.get("type",""), "bg-slate-500")} h-1.5 rounded-full" style="width:{int(e.get('intensity',0)*100)}%"></div>
          </div>
          <span class="text-slate-500 w-7 text-right shrink-0">{int(e.get('intensity',0)*100)}%</span>
        </div>"""
        for e in emotions
    )


def _news_card(item: dict) -> str:
    title = _escape(item.get("title", ""))
    url = item.get("url", "")
    source_type = item.get("source_type", "X")
    source_name = _escape(item.get("source_name", ""))
    published_at = _escape(item.get("published_at", ""))
    genre_tags = item.get("genre_tags", [])
    emotions = item.get("emotions", [])
    formats = item.get("formats", [])
    angle = _escape(item.get("angle_memo", ""))
    summary = _escape(item.get("summary", ""))
    x_rt = item.get("x_rt_count", 0)
    x_like = item.get("x_like_count", 0)

    badge_cls = _SOURCE_BADGE.get(source_type, _SOURCE_BADGE["X"])
    source_icon = {"教育新聞": "📰", "地方新聞": "🗞️", "X": "𝕏"}.get(source_type, "📄")

    # ジャンルタグ（# なし）
    tags_html = "".join(
        f'<span class="rounded-full bg-slate-700/70 px-2 py-0.5 text-xs text-slate-300">{_escape(t)}</span>'
        for t in genre_tags
    )

    # 感情チップ（バーではなくピル形式）
    _EMOTION_CHIP = {
        "怒り": "bg-red-900/70 text-red-300", "不安": "bg-amber-900/70 text-amber-300",
        "共感": "bg-emerald-900/70 text-emerald-300", "驚き": "bg-purple-900/70 text-purple-300",
        "悲しみ": "bg-blue-900/70 text-blue-300", "感動": "bg-pink-900/70 text-pink-300",
        "期待": "bg-sky-900/70 text-sky-300", "落胆": "bg-slate-700 text-slate-400",
        "懐疑": "bg-orange-900/70 text-orange-300", "疲労感": "bg-zinc-700 text-zinc-300",
        "温かさ": "bg-rose-900/70 text-rose-300",
    }
    # 最も強い感情上位2つだけ表示
    sorted_emotions = sorted(emotions, key=lambda e: e.get("intensity", 0), reverse=True)[:2]
    emotion_chips = "".join(
        f'<span class="rounded-full px-2 py-0.5 text-xs font-medium {_EMOTION_CHIP.get(e.get("type",""), "bg-slate-700 text-slate-300")}">{_escape(e.get("type",""))}</span>'
        for e in sorted_emotions
    )

    # 向いている形式バッジ
    fmt_html = "".join(
        f'<span class="rounded-full px-2 py-0.5 text-xs {_FORMAT_BADGE_NEWS.get(f, "bg-slate-700 text-slate-300")}">{_escape(f)}</span>'
        for f in formats
    )

    # X統計（小さく）
    x_stats = ""
    if x_rt or x_like:
        x_stats = f'<span class="text-xs text-slate-500">🔁{x_rt:,}  ❤️{x_like:,}</span>'

    url_html = (
        f'<a href="{_escape(url)}" target="_blank" rel="noopener" '
        f'class="shrink-0 rounded-lg bg-slate-700/60 hover:bg-slate-600/60 px-2 py-1 text-xs text-blue-400 transition-colors">🔗 開く</a>'
    ) if url else ""

    return f"""
<div class="rounded-2xl border border-slate-700/50 bg-[#111827] p-4 flex flex-col gap-3 hover:border-slate-600/70 transition-colors">

  <!-- ヘッダー行: 出典 + 日付 + X統計 + リンク -->
  <div class="flex items-center gap-2 flex-wrap">
    <span class="rounded-full border px-2 py-0.5 text-xs font-medium {badge_cls}">{source_icon} {_escape(source_type)}</span>
    <span class="text-xs text-slate-500 truncate flex-1">{source_name}</span>
    {x_stats}
    {url_html}
  </div>

  <!-- タイトル -->
  <h3 class="text-base font-bold text-slate-100 leading-snug">{title}</h3>

  <!-- 概要 -->
  <p class="text-xs text-slate-400 leading-relaxed">{summary}</p>

  <!-- ジャンル + 感情（一目でわかる行） -->
  <div class="flex flex-wrap gap-1 items-center">
    {tags_html}
    <span class="text-slate-600 text-xs mx-1">|</span>
    {emotion_chips}
  </div>

  <!-- 向いている形式 -->
  <div class="flex flex-wrap gap-1">{fmt_html}</div>

  <!-- 切り口メモ（最重要情報） -->
  <div class="rounded-xl bg-slate-800/80 border-l-2 border-violet-500 px-3 py-2">
    <p class="text-xs font-semibold text-violet-400 mb-0.5">✏️ 切り口</p>
    <p class="text-xs text-slate-300 leading-relaxed">{angle}</p>
  </div>

</div>"""


# ─────────────────────────────────────────────────────────────
# PAGE 3: ホットコメント
# ─────────────────────────────────────────────────────────────

def _anti_comment_card(c: dict) -> str:
    post_title = _escape(c.get("post_title", ""))
    post_url = c.get("post_url", "")
    comment = _escape(c.get("comment", ""))
    username = _escape(c.get("username", ""))
    ts = _escape(c.get("timestamp", ""))
    likes = c.get("likes", 0)
    emotion = _escape(c.get("emotion", ""))
    handling = _escape(c.get("handling_note", ""))
    potential = _escape(c.get("content_potential", ""))

    url_html = f'<a href="{_escape(post_url)}" target="_blank" class="text-xs text-blue-400 hover:text-blue-300 underline">🔗 投稿を開く</a>' if post_url else ""

    return f"""
<div class="rounded-2xl border border-red-700/40 bg-gradient-to-br from-[#1f0a0a] to-[#2a0f0f] p-5 flex flex-col gap-3">
  <div>
    <div class="flex items-center gap-2 mb-1">
      <span class="rounded-full bg-red-900/60 border border-red-700/40 px-2 py-0.5 text-xs text-red-300">😡 アンチ系</span>
      <span class="text-xs text-slate-500">{ts}</span>
      <span class="ml-auto text-xs text-slate-500">❤️ {likes}</span>
    </div>
    <p class="text-xs text-slate-500 mb-0.5">投稿：「{post_title}」</p>
    {url_html}
  </div>
  <blockquote class="border-l-2 border-red-500 pl-3 py-1 bg-red-950/40 rounded-r-xl">
    <p class="text-sm text-slate-200 leading-relaxed">「{comment}」</p>
    <footer class="text-xs text-slate-500 mt-1">— @{username}</footer>
  </blockquote>
  <div class="flex items-center gap-2">
    <span class="text-xs text-slate-500">感情：</span>
    <span class="rounded-full bg-slate-700/50 px-2 py-0.5 text-xs text-slate-300">{emotion}</span>
  </div>
  <div class="rounded-xl bg-amber-900/20 border border-amber-700/30 px-3 py-2">
    <p class="text-xs font-semibold text-amber-400 mb-1">🛡️ 対応メモ</p>
    <p class="text-xs text-slate-300 leading-relaxed">{handling}</p>
  </div>
  {f'<div class="rounded-xl bg-violet-900/20 border border-violet-700/30 px-3 py-2"><p class="text-xs font-semibold text-violet-400 mb-1">💡 コンテンツ活用ポイント</p><p class="text-xs text-slate-300 leading-relaxed">{potential}</p></div>' if potential else ""}
</div>"""


def _consultation_card(c: dict) -> str:
    post_title = _escape(c.get("post_title", ""))
    post_url = c.get("post_url", "")
    comment = _escape(c.get("comment", ""))
    username = _escape(c.get("username", ""))
    ts = _escape(c.get("timestamp", ""))
    likes = c.get("likes", 0)
    topic = _escape(c.get("topic", ""))
    emotion = _escape(c.get("emotion", ""))
    potential = _escape(c.get("content_potential", ""))
    suggested = _escape(c.get("suggested_use", ""))
    rec_formats = c.get("recommended_format", [])

    url_html = f'<a href="{_escape(post_url)}" target="_blank" class="text-xs text-blue-400 hover:text-blue-300 underline">🔗 投稿を開く</a>' if post_url else ""
    _FORMAT_BADGE2 = {"リール": "bg-pink-900/70 text-pink-300", "フィード": "bg-violet-900/70 text-violet-300",
                      "YouTubeライブ": "bg-red-900/70 text-red-300", "スタエフ": "bg-sky-900/70 text-sky-300",
                      "Instagram": "bg-violet-900/70 text-violet-300"}
    fmt_html = "".join(
        f'<span class="rounded-full px-2 py-0.5 text-xs {_FORMAT_BADGE2.get(f, "bg-slate-700 text-slate-300")}">{_escape(f)}</span>'
        for f in rec_formats
    )
    potential_color = {"高": "text-emerald-300", "非常に高": "text-amber-300"}.get(potential, "text-slate-300")

    return f"""
<div class="rounded-2xl border border-sky-700/40 bg-gradient-to-br from-[#07182a] to-[#0c1e30] p-5 flex flex-col gap-3">
  <div>
    <div class="flex items-center gap-2 mb-1">
      <span class="rounded-full bg-sky-900/60 border border-sky-700/40 px-2 py-0.5 text-xs text-sky-300">📨 長文相談</span>
      <span class="text-xs text-slate-500">{ts}</span>
      <span class="ml-auto text-xs text-slate-500">❤️ {likes}</span>
    </div>
    <p class="text-xs text-slate-500 mb-0.5">投稿：「{post_title}」</p>
    {url_html}
  </div>
  {f'<div class="flex items-center gap-2"><span class="text-xs text-slate-500 shrink-0">テーマ：</span><span class="rounded-full bg-slate-700/50 px-2 py-0.5 text-xs text-slate-200 font-medium">{topic}</span><span class="text-xs text-slate-400">/{emotion}</span></div>' if topic else ""}
  <blockquote class="border-l-2 border-sky-500 pl-3 py-1 bg-sky-950/40 rounded-r-xl">
    <p class="text-sm text-slate-200 leading-relaxed">「{comment}」</p>
    <footer class="text-xs text-slate-500 mt-1">— @{username}</footer>
  </blockquote>
  <div class="flex items-center gap-2">
    <span class="text-xs text-slate-500">コンテンツ化ポテンシャル：</span>
    <span class="text-xs font-bold {potential_color}">{potential}</span>
  </div>
  <div class="rounded-xl bg-emerald-900/20 border border-emerald-700/30 px-3 py-2">
    <p class="text-xs font-semibold text-emerald-400 mb-1">🎙️ 活用提案</p>
    <p class="text-xs text-slate-300 leading-relaxed">{suggested}</p>
  </div>
  {f'<div><p class="text-xs text-slate-500 mb-1">おすすめ形式：</p><div class="flex flex-wrap gap-1">{fmt_html}</div></div>' if fmt_html else ""}
</div>"""


# ─────────────────────────────────────────────────────────────
# PAGE 4: 昨年同時期のバズ投稿
# ─────────────────────────────────────────────────────────────

def _past_post_card(p: dict) -> str:
    title = _escape(p.get("title", ""))
    period = _escape(p.get("period", ""))
    url = p.get("url", "")
    likes = p.get("like_count", 0)
    comments = p.get("comments_count", 0)
    engagement = p.get("engagement", 0)
    snippet = _escape(p.get("caption_snippet", ""))
    what_worked = _escape(p.get("what_worked", ""))
    repurpose = _escape(p.get("repurpose_idea", ""))
    overlap = p.get("trend_overlap", [])
    seasonal = p.get("seasonal_match", False)
    media_type = p.get("media_type", "IMAGE")

    tags_html = "".join(
        f'<span class="rounded-full bg-slate-700/60 border border-slate-600/40 px-2 py-0.5 text-xs text-slate-300">{_escape(t)}</span>'
        for t in overlap
    )
    url_html = f'<a href="{_escape(url)}" target="_blank" class="text-xs text-blue-400 hover:text-blue-300 underline">🔗 投稿を開く</a>' if url else ""
    media_icon = {"IMAGE": "📸", "VIDEO": "🎬", "CAROUSEL_ALBUM": "📑"}.get(media_type, "📸")
    seasonal_badge = '<span class="rounded-full bg-emerald-900/60 border border-emerald-700/40 px-2 py-0.5 text-xs text-emerald-300">🗓️ 今年も旬</span>' if seasonal else ""

    return f"""
<div class="rounded-2xl border border-amber-700/40 bg-gradient-to-br from-[#1a1500] to-[#221d00] p-5 flex flex-col gap-3">
  <div>
    <div class="flex flex-wrap items-center gap-2 mb-1">
      <span class="text-xs text-amber-400 font-medium">{period}</span>
      <span class="text-xs text-slate-500">{media_icon} {media_type}</span>
      {seasonal_badge}
    </div>
    <h3 class="text-sm font-bold text-amber-200 leading-snug">{title}</h3>
    {url_html}
  </div>
  <div class="grid grid-cols-3 gap-2 text-center">
    <div class="rounded-xl bg-slate-800/60 py-2">
      <p class="text-lg font-black text-violet-300">{likes:,}</p>
      <p class="text-xs text-slate-500">いいね</p>
    </div>
    <div class="rounded-xl bg-slate-800/60 py-2">
      <p class="text-lg font-black text-pink-300">{comments:,}</p>
      <p class="text-xs text-slate-500">コメント</p>
    </div>
    <div class="rounded-xl bg-slate-800/60 py-2">
      <p class="text-lg font-black text-amber-300">{engagement:,}</p>
      <p class="text-xs text-slate-500">エンゲージメント</p>
    </div>
  </div>
  <div class="rounded-xl bg-slate-800/60 p-3">
    <p class="text-xs text-slate-500 mb-1">キャプション冒頭：</p>
    <p class="text-xs text-slate-300 font-mono whitespace-pre-line leading-relaxed">{snippet}</p>
  </div>
  <div class="flex flex-wrap gap-1">{tags_html}</div>
  <div class="rounded-xl bg-amber-900/20 border border-amber-700/30 px-3 py-2">
    <p class="text-xs font-semibold text-amber-400 mb-1">✅ 伸びた理由</p>
    <p class="text-xs text-slate-300 leading-relaxed">{what_worked}</p>
  </div>
  <div class="rounded-xl bg-violet-900/20 border border-violet-700/30 px-3 py-2">
    <p class="text-xs font-semibold text-violet-400 mb-1">♻️ 今年の転用アイデア</p>
    <p class="text-xs text-slate-300 leading-relaxed">{repurpose}</p>
  </div>
</div>"""


# ─────────────────────────────────────────────────────────────
# メイン生成関数
# ─────────────────────────────────────────────────────────────

def generate_html_report(
    report: dict,
    account_name: str = "ダイ先生",
    kpi: dict = None,
    today: date = None,
    news_items: list = None,
    top3_ideas: list = None,
    dual_summary: dict = None,
    hot_comments: dict = None,
    past_posts: list = None,
) -> str:
    if today is None:
        today = date.today()
    kpi = kpi or {}
    news_items = news_items or []
    top3_ideas = top3_ideas or []
    dual_summary = dual_summary or {}
    hot_comments = hot_comments or {}
    past_posts = past_posts or []

    report_date = _escape(report.get("date", today.strftime("%Y年%m月%d日")))
    summary = _escape(report.get("summary", ""))
    insights = report.get("insights", [])

    instagram_ideas = report.get("instagram_ideas", [])
    if not instagram_ideas:
        for idea in report.get("feed_ideas", []):
            instagram_ideas.append({**idea, "format_suggestion": "フィード推奨"})
        for idea in report.get("reel_ideas", []):
            instagram_ideas.append({**idea, "format_suggestion": "リール推奨"})

    stafy_topics = report.get("stafy_topics", [])
    yt_topics = report.get("youtube_live_topics", [])
    generated_at = datetime.now().strftime("%Y/%m/%d %H:%M")

    # ─── Page 1 HTML
    dual_html = _dual_summary(dual_summary) if dual_summary else ""
    top3_html = "".join(_top3_card(i + 1, item) for i, item in enumerate(top3_ideas[:3]))
    insights_html = "".join(_insight_pill(ins) for ins in insights)
    instagram_html = "".join(_instagram_card(i + 1, idea) for i, idea in enumerate(instagram_ideas))
    stafy_html = "".join(_stafy_card(i + 1, t) for i, t in enumerate(stafy_topics))
    yt_html = "".join(_youtube_card(i + 1, t) for i, t in enumerate(yt_topics))

    # ─── Page 2 HTML
    news_html = "".join(_news_card(item) for item in news_items)

    # ─── Page 3 HTML
    anti_html = "".join(_anti_comment_card(c) for c in hot_comments.get("anti", []))
    consult_html = "".join(_consultation_card(c) for c in hot_comments.get("long_consultation", []))

    # ─── Page 4 HTML
    past_html = "".join(_past_post_card(p) for p in past_posts)
    past_seasonal = [p for p in past_posts if p.get("seasonal_match")]

    return f"""<!DOCTYPE html>
<html lang="ja" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{_escape(account_name)} コンテンツ分析レポート — {report_date}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>tailwind.config = {{ darkMode: 'class' }}</script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet" />
  <style>
    body {{ font-family: 'Noto Sans JP', sans-serif; }}
    .gradient-text {{
      background: linear-gradient(135deg, #c084fc 0%, #f472b6 50%, #60a5fa 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    }}
    .tab-btn {{ transition: all 0.2s; }}
    .tab-btn.active {{
      background: linear-gradient(135deg, #7c3aed, #db2777);
      color: white; border-color: transparent;
    }}
    [data-panel] {{ display: none; }}
    [data-panel].active {{ display: block; }}
  </style>
</head>
<body class="min-h-screen bg-[#0a0f1e] text-slate-100">

<!-- ── Sticky header + tab nav ── -->
<header class="sticky top-0 z-50 border-b border-slate-800 bg-[#0d1424]/95 backdrop-blur-sm">
  <div class="mx-auto max-w-7xl px-4">
    <div class="flex items-center gap-3 py-3 border-b border-slate-800/60">
      <div class="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-pink-600 text-white font-black text-sm">D</div>
      <div>
        <span class="font-bold text-slate-200 text-sm">{_escape(account_name)}</span>
        <span class="text-slate-500 text-xs ml-2">コンテンツ分析</span>
      </div>
      <div class="ml-auto flex items-center gap-3">
        <span class="text-xs text-slate-500 hidden sm:block">{report_date}</span>
        <span class="text-xs text-slate-600">{generated_at} 生成</span>
      </div>
    </div>
    <!-- Tab buttons -->
    <nav class="flex gap-1 py-2 overflow-x-auto">
      <button data-tab-btn="1" onclick="switchTab(1)"
        class="tab-btn active flex items-center gap-1.5 rounded-xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 whitespace-nowrap">
        📊 ダッシュボード
      </button>
      <button data-tab-btn="2" onclick="switchTab(2)"
        class="tab-btn flex items-center gap-1.5 rounded-xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 whitespace-nowrap">
        📰 外部トレンド
      </button>
      <button data-tab-btn="3" onclick="switchTab(3)"
        class="tab-btn flex items-center gap-1.5 rounded-xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 whitespace-nowrap">
        💬 ホットコメント
      </button>
      <button data-tab-btn="4" onclick="switchTab(4)"
        class="tab-btn flex items-center gap-1.5 rounded-xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 whitespace-nowrap">
        📅 昨年同時期
      </button>
    </nav>
  </div>
</header>

<main class="mx-auto max-w-7xl px-4 py-8">

<!-- ════════════════════════════════════════════════════════ PAGE 1 -->
<div data-panel="1" class="active space-y-10">

  <!-- タイトル -->
  <div class="text-center space-y-3">
    <p class="text-xs font-medium text-slate-500 tracking-widest uppercase">Daily Content Report</p>
    <h1 class="text-3xl font-black gradient-text">{report_date}</h1>
    {f'<div class="mx-auto max-w-2xl rounded-2xl bg-gradient-to-r from-violet-900/40 to-pink-900/40 border border-violet-500/30 px-6 py-4"><p class="text-sm text-slate-300 leading-relaxed">📌 <span class="font-semibold text-violet-200">今日のまとめ：</span>{summary}</p></div>' if summary else ""}
  </div>

  <!-- デュアルサマリー -->
  {dual_html}

  <!-- TOP 3 -->
  {f'''<section>
    <div class="mb-5 flex items-center gap-3">
      <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-600/20 border border-amber-500/40 text-lg">🏆</div>
      <div>
        <p class="text-xs font-semibold uppercase tracking-widest text-amber-400">今日のイチオシ</p>
        <h2 class="text-lg font-bold text-amber-200">今日いちばん伸びそうなネタ 3選</h2>
      </div>
      <p class="ml-auto text-xs text-slate-500 hidden md:block text-right leading-relaxed">過去の類似投稿・季節一致・ニュース接続<br>コメント熱量・外部トレンドの複合スコア</p>
    </div>
    <div class="grid gap-5 md:grid-cols-3">{top3_html}</div>
  </section>''' if top3_ideas else ""}

  <!-- インサイト -->
  {f'''<section>
    <div class="mb-4 flex items-center gap-3">
      <div class="h-px flex-1 bg-slate-800"></div>
      <h2 class="text-xs font-bold uppercase tracking-widest text-amber-400">🔍 Data Insights</h2>
      <div class="h-px flex-1 bg-slate-800"></div>
    </div>
    <div class="grid gap-3 sm:grid-cols-3">{insights_html}</div>
  </section>''' if insights else ""}

  <!-- Instagram ネタ案 -->
  {f'''<section>
    <div class="mb-5 flex items-center gap-3">
      <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-violet-600/20 border border-violet-500/40 text-lg">📱</div>
      <div>
        <p class="text-xs font-semibold uppercase tracking-widest text-violet-400">Instagram Content Ideas</p>
        <h2 class="text-lg font-bold text-violet-200">Instagram 投稿ネタ案</h2>
      </div>
      <span class="ml-auto rounded-full bg-violet-900/50 px-3 py-1 text-xs text-violet-300">{len(instagram_ideas)}件</span>
    </div>
    <div class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">{instagram_html}</div>
  </section>''' if instagram_ideas else ""}

  <!-- スタエフ -->
  {f'''<section>
    <div class="mb-5 flex items-center gap-3">
      <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-sky-600/20 border border-sky-500/40 text-lg">🎙️</div>
      <div>
        <p class="text-xs font-semibold uppercase tracking-widest text-sky-400">Stand.fm Topics</p>
        <h2 class="text-lg font-bold text-sky-200">スタエフ トークネタ</h2>
      </div>
      <span class="ml-auto rounded-full bg-sky-900/50 px-3 py-1 text-xs text-sky-300">{len(stafy_topics)}件</span>
    </div>
    <div class="grid gap-5 md:grid-cols-2">{stafy_html}</div>
  </section>''' if stafy_topics else ""}


</div>

<!-- ════════════════════════════════════════════════════════ PAGE 2 -->
<div data-panel="2" class="space-y-8">
  <div class="flex items-center gap-3 mb-2">
    <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-orange-600/20 border border-orange-500/40 text-lg">📰</div>
    <div>
      <p class="text-xs font-semibold uppercase tracking-widest text-orange-400">外部トレンド・教育ニュース</p>
      <h2 class="text-lg font-bold text-orange-200">外部トレンド・教育ニュース</h2>
    </div>
    <span class="ml-auto rounded-full bg-orange-900/50 px-3 py-1 text-xs text-orange-300">{len(news_items)}件</span>
  </div>
  <div class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">{news_html}</div>
</div>

<!-- ════════════════════════════════════════════════════════ PAGE 3 -->
<div data-panel="3" class="space-y-10">
  <div class="flex items-center gap-3">
    <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-rose-600/20 border border-rose-500/40 text-lg">💬</div>
    <div>
      <p class="text-xs font-semibold uppercase tracking-widest text-rose-400">直近7日間 注目コメント</p>
      <h2 class="text-lg font-bold text-rose-200">一週間以内のホットコメント</h2>
    </div>
  </div>

  <!-- アンチ系 -->
  {f'''<section>
    <div class="mb-4 flex items-center gap-2">
      <span class="text-base">😡</span>
      <h3 class="text-base font-bold text-red-300">アンチ系コメント</h3>
      <span class="rounded-full bg-red-900/50 px-2 py-0.5 text-xs text-red-300">{len(hot_comments.get("anti",[]))}件</span>
      <p class="ml-2 text-xs text-slate-500">批判・懐疑・反論系のコメントをピックアップ</p>
    </div>
    <div class="grid gap-5 md:grid-cols-2">{anti_html}</div>
  </section>''' if hot_comments.get("anti") else ""}

  <div class="h-px bg-gradient-to-r from-transparent via-slate-700 to-transparent"></div>

  <!-- 長文相談系 -->
  {f'''<section>
    <div class="mb-4 flex items-center gap-2">
      <span class="text-base">📨</span>
      <h3 class="text-base font-bold text-sky-300">長文相談系コメント</h3>
      <span class="rounded-full bg-sky-900/50 px-2 py-0.5 text-xs text-sky-300">{len(hot_comments.get("long_consultation",[]))}件</span>
      <p class="ml-2 text-xs text-slate-500">コンテンツ化ポテンシャルの高い相談コメント</p>
    </div>
    <div class="grid gap-5 md:grid-cols-2">{consult_html}</div>
  </section>''' if hot_comments.get("long_consultation") else ""}
</div>

<!-- ════════════════════════════════════════════════════════ PAGE 4 -->
<div data-panel="4" class="space-y-8">
  <div class="flex items-center gap-3">
    <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-600/20 border border-amber-500/40 text-lg">📅</div>
    <div>
      <p class="text-xs font-semibold uppercase tracking-widest text-amber-400">昨年同時期 バズり投稿</p>
      <h2 class="text-lg font-bold text-amber-200">昨年同時期のバズ投稿</h2>
    </div>
    {f'<span class="ml-auto rounded-full bg-emerald-900/50 px-3 py-1 text-xs text-emerald-300">🗓️ 今年も旬 {len(past_seasonal)}件</span>' if past_seasonal else ""}
  </div>
  <p class="text-sm text-slate-500 -mt-6">昨年の同時期（4月前後）に高エンゲージメントを記録した投稿をピックアップ。転用・リメイクの参考にしてください。</p>
  <div class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">{past_html}</div>
</div>

</main>

<footer class="mt-16 border-t border-slate-800 bg-[#0d1424]/80 py-6">
  <div class="mx-auto max-w-7xl px-4 text-center">
    <p class="text-xs text-slate-600">Generated by {_escape(account_name)} コンテンツ分析ツール powered by GPT-4o — {generated_at}</p>
  </div>
</footer>

<script>
function switchTab(id) {{
  document.querySelectorAll('[data-panel]').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('[data-tab-btn]').forEach(b => b.classList.remove('active'));
  document.querySelector('[data-panel="' + id + '"]').classList.add('active');
  document.querySelector('[data-tab-btn="' + id + '"]').classList.add('active');
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
}}
</script>
</body>
</html>"""
