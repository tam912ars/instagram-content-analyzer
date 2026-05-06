/**
 * build-report.js
 * HTMLレポートを生成する
 * Phase 1: AI不使用・RSS取得データのみ表示
 * Phase 2: Gemini API による要約・投稿案を追加予定
 */

// HTMLエスケープ
function esc(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ランク別スタイル定義
const RANK_STYLES = {
  1: { badge: 'bg-sky-500',    icon: '🥇', border: 'border-sky-400',    header: 'bg-sky-50',    label: 'text-sky-500' },
  2: { badge: 'bg-indigo-500', icon: '🥈', border: 'border-indigo-400', header: 'bg-indigo-50', label: 'text-indigo-500' },
  3: { badge: 'bg-violet-500', icon: '🥉', border: 'border-violet-400', header: 'bg-violet-50', label: 'text-violet-500' },
};

function newsCard(rank, article) {
  const s = RANK_STYLES[rank] ?? RANK_STYLES[3];
  const linkHtml = article.url && article.url !== '#'
    ? `<a href="${esc(article.url)}" target="_blank" rel="noopener"
          class="news-link inline-flex items-center gap-1 text-xs text-sky-600 font-medium
                 hover:text-sky-800 transition-colors focus:outline-none focus:ring-2
                 focus:ring-sky-400 rounded"
          aria-label="記事「${esc(article.title)}」を読む">
         🔗 記事を読む →
       </a>`
    : `<span class="text-xs text-slate-400">リンクなし</span>`;

  return `
<article class="news-card news-card--0${rank} bg-white rounded-2xl shadow-sm border border-slate-200
                border-l-4 ${s.border} overflow-hidden flex flex-col"
         data-component="news-card" data-index="${rank}">

  <!-- カードヘッダー -->
  <div class="${s.header} px-4 py-2.5 flex items-center justify-between">
    <div class="flex items-center gap-2">
      <span class="text-xl" aria-hidden="true">${s.icon}</span>
      <span class="text-xs font-black tracking-widest text-slate-600">NEWS 0${rank}</span>
    </div>
    <span class="rounded-full ${s.badge} text-white text-xs px-2 py-0.5 font-bold">${rank}位</span>
  </div>

  <!-- カードボディ -->
  <div class="px-4 py-4 flex flex-col gap-3 flex-1">

    <!-- ① タイトル -->
    <div>
      <p class="text-xs font-bold ${s.label} uppercase tracking-wider mb-1">① タイトル</p>
      <h3 class="news-title text-sm font-bold text-slate-800 leading-snug">
        ${esc(article.title)}
      </h3>
    </div>

    <!-- ② 概要 -->
    <div>
      <p class="text-xs font-bold ${s.label} uppercase tracking-wider mb-1">② 概要</p>
      <p class="news-summary text-xs text-slate-500 leading-relaxed">
        ${esc(article.description) || '（概要なし）'}
      </p>
    </div>

    <!-- 出典 -->
    ${article.source ? `<p class="text-xs text-slate-400">出典: ${esc(article.source)}</p>` : ''}

    <!-- リンク -->
    <div class="mt-auto pt-2 border-t border-slate-100">
      ${linkHtml}
    </div>
  </div>
</article>`;
}

function postPlaceholder(num, type) {
  const colors = ['sky', 'indigo', 'violet', 'emerald', 'rose'];
  const c = colors[num - 1] ?? 'slate';
  return `
<article class="post-card post-card--0${num} bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
  <div class="flex items-stretch">
    <div class="w-1.5 shrink-0 bg-${c}-400" aria-hidden="true"></div>
    <div class="flex-1 p-5">
      <div class="flex items-start gap-4">
        <div class="post-number flex h-10 w-10 shrink-0 items-center justify-center
                    rounded-xl bg-${c}-100 text-${c}-700 text-sm font-black"
             aria-label="投稿案 0${num}">
          0${num}
        </div>
        <div class="flex-1 min-w-0">
          <p class="post-type text-sm font-bold text-slate-800">${esc(type)}</p>
          <p class="post-content mt-2 text-sm text-slate-400 leading-relaxed
                    bg-slate-50 rounded-lg px-3 py-2 border border-slate-100 italic">
            🤖 Phase 2 で Gemini AI により自動生成されます
          </p>
        </div>
        <span class="shrink-0 rounded-full bg-slate-100 text-slate-500 border border-slate-200
                     px-2.5 py-1 text-xs font-medium whitespace-nowrap">準備中</span>
      </div>
    </div>
  </div>
</article>`;
}

const POST_TYPES = [
  'ニュース × 当事者感情 × 問い',
  '教師の働き方への問題提起',
  '現場教師への共感ポスト',
  '社会への問いを投げるポスト',
  'LINE導線・相談導線につなげるポスト',
];

export function buildReport(articles, isoDate) {
  const d        = new Date(isoDate + 'T00:00:00+09:00');
  const dateJa   = d.toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' });
  const weekday  = ['日', '月', '火', '水', '木', '金', '土'][d.getDay()];
  const genTime  = new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' });

  const newsHtml  = articles.map((a, i) => newsCard(i + 1, a)).join('\n');
  const postsHtml = POST_TYPES.map((t, i) => postPlaceholder(i + 1, t)).join('\n');

  return `<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ダイ先生 毎朝自動レポート — ${esc(dateJa)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            sans: ["'Noto Sans JP'", 'ui-sans-serif', 'system-ui', '-apple-system', 'sans-serif'],
          },
        },
      },
    }
  </script>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet" />
</head>

<body class="min-h-screen bg-slate-50 font-sans text-slate-700">

  <!-- ── Sticky header ── -->
  <header class="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-slate-200 shadow-sm">
    <div class="h-1 bg-gradient-to-r from-sky-400 via-indigo-500 to-violet-500" aria-hidden="true"></div>
    <div class="mx-auto max-w-3xl px-4 py-3 flex items-center gap-3">
      <div class="flex h-8 w-8 items-center justify-center rounded-xl
                  bg-gradient-to-br from-indigo-700 via-violet-700 to-purple-700
                  text-white font-black text-sm shrink-0" aria-hidden="true">D</div>
      <div class="flex-1 min-w-0">
        <span class="font-bold text-slate-800 text-sm">ダイ先生</span>
        <span class="text-slate-400 text-xs ml-2">教師向けニュースレポート</span>
      </div>
      <span class="text-xs text-slate-500 shrink-0 hidden sm:block">${esc(dateJa)}（${weekday}）</span>
    </div>
  </header>

  <!-- ── Hero ── -->
  <div class="bg-gradient-to-br from-indigo-700 via-violet-700 to-purple-700 text-white">
    <div class="mx-auto max-w-3xl px-6 py-10">
      <p class="text-indigo-200 text-xs font-semibold tracking-[0.2em] uppercase mb-3">
        Daily Education News
      </p>
      <h1 class="text-3xl sm:text-4xl font-black mb-2 leading-tight">
        ${esc(dateJa)}（${weekday}）
      </h1>
      <p class="text-indigo-200 text-sm">
        教育ニュースから注目の
        <span class="text-amber-300 font-bold">Top ${articles.length}</span>
        をピックアップ
      </p>
    </div>
  </div>

  <main class="mx-auto max-w-3xl px-4 py-8 space-y-10">

    <!-- ── STEP 1: ニュース ── -->
    <div class="space-y-4">
      <div class="flex items-center gap-3" role="heading" aria-level="2">
        <div class="flex items-center gap-2 shrink-0">
          <span class="flex h-7 w-7 items-center justify-center rounded-full
                       bg-sky-500 text-white text-xs font-black" aria-hidden="true">1</span>
          <span class="text-sm font-bold text-slate-600">ニュース収集</span>
        </div>
        <div class="flex-1 h-px bg-slate-200" aria-hidden="true"></div>
        <span class="text-xs text-slate-400 shrink-0">Top ${articles.length} ピックアップ</span>
      </div>

      <section class="news-section grid grid-cols-1 sm:grid-cols-3 gap-5"
               aria-label="収集したニュース一覧">
        ${newsHtml}
      </section>
    </div>

    <!-- ── STEP 2: 投稿案 ── -->
    <div class="space-y-4">
      <div class="flex items-center gap-3" role="heading" aria-level="2">
        <div class="flex items-center gap-2 shrink-0">
          <span class="flex h-7 w-7 items-center justify-center rounded-full
                       bg-indigo-500 text-white text-xs font-black" aria-hidden="true">2</span>
          <span class="text-sm font-bold text-slate-600">投稿案生成</span>
        </div>
        <div class="flex-1 h-px bg-slate-200" aria-hidden="true"></div>
        <span class="text-xs text-slate-400 shrink-0">X / Threads</span>
      </div>

      <section class="post-section space-y-4" aria-label="投稿案一覧">
        <div class="rounded-2xl bg-gradient-to-r from-indigo-500 to-violet-500
                    px-6 py-4 flex items-center justify-between">
          <div>
            <p class="text-xs font-semibold text-indigo-200 tracking-wider uppercase mb-0.5">
              Auto Generated
            </p>
            <p class="text-lg font-black text-white">X / Threads 投稿案 自動生成</p>
          </div>
          <span class="text-3xl opacity-60" aria-hidden="true">✍️</span>
        </div>
        <div class="space-y-3">
          ${postsHtml}
        </div>
      </section>
    </div>

    <!-- ── Phase 1 注記 ── -->
    <div class="rounded-xl bg-amber-50 border border-amber-200 px-4 py-3
                flex items-start gap-3">
      <span class="text-base shrink-0 mt-0.5" aria-hidden="true">📌</span>
      <p class="text-xs text-amber-700 leading-relaxed">
        <strong>Phase 1</strong>：RSS取得・HTML生成・GitHub Pages 公開まで完了。<br>
        <strong>Phase 2</strong> で Gemini AI による要約・投稿案生成を追加予定です。
      </p>
    </div>

  </main>

  <footer class="mt-8 border-t border-slate-200 bg-white py-6">
    <div class="mx-auto max-w-3xl px-4 flex flex-col sm:flex-row
                items-center justify-between gap-2 text-xs text-slate-400">
      <p>ダイ先生 毎朝自動レポートツール</p>
      <p>生成日時: ${esc(genTime)}</p>
    </div>
  </footer>

</body>
</html>`;
}
