/**
 * build-report.js
 * HTMLレポートを生成する
 * Phase 1: AI不使用・RSS取得データのみ表示
 * Phase 2: Gemini AI による要約・投稿案を表示（現在）
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


    <!-- カテゴリ + 出典 -->
    <div class="flex items-center gap-2 flex-wrap">
      ${article.category
        ? `<span class="text-xs bg-${s.badge.replace('bg-','').replace('-500','')}-50 text-${s.label.replace('text-','')} border border-${s.border.replace('border-','')} rounded-full px-2 py-0.5 font-medium">${esc(article.category)}</span>`
        : ''
      }
      ${article.source ? `<p class="text-xs text-slate-400">出典: ${esc(article.source)}</p>` : ''}
    </div>

    <!-- リンク -->
    <div class="mt-auto pt-2 border-t border-slate-100">
      ${linkHtml}
    </div>
  </div>
</article>`;
}

/**
 * 投稿案カード（ニュース1本 = Threads + X の2カラム）
 * @param {number} num    - 1〜3（ニュース番号）
 * @param {object} post   - { emotion, weight, threads, x } または null
 */
function postCard(num, post = null) {
  const colors = ['sky', 'indigo', 'violet'];
  const c = colors[num - 1] ?? 'slate';
  const isAI = post && post.threads && !post.threads.startsWith('（AI生成に失敗');

  const weightBadge = post?.weight === '軽い'
    ? `<span class="text-xs rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 font-medium">軽いテーマ</span>`
    : `<span class="text-xs rounded-full bg-rose-50 text-rose-700 border border-rose-200 px-2 py-0.5 font-medium">重いテーマ</span>`;

  const aiBadge = isAI
    ? `<span class="shrink-0 rounded-full bg-green-100 text-green-700 border border-green-200 px-2.5 py-1 text-xs font-medium">AI生成</span>`
    : `<span class="shrink-0 rounded-full bg-slate-100 text-slate-500 border border-slate-200 px-2.5 py-1 text-xs font-medium">準備中</span>`;

  const placeholder = `<p class="text-sm text-slate-400 italic bg-slate-50 rounded-lg px-3 py-2 border border-slate-100">
      🤖 GROQ_API_KEY を設定すると AI が自動生成します
    </p>`;

  const threadsBlock = isAI
    ? `<div class="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap bg-indigo-50 rounded-lg px-3 py-3 border border-indigo-100">${esc(post.threads)}</div>
       <button onclick="copyText(this)" data-text="${esc(post.threads)}"
               class="mt-1.5 text-xs text-indigo-500 hover:text-indigo-700 font-medium transition-colors">
         コピー
       </button>`
    : placeholder;

  const xBlock = isAI
    ? `<div class="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap bg-sky-50 rounded-lg px-3 py-3 border border-sky-100">${esc(post.x)}</div>
       <button onclick="copyText(this)" data-text="${esc(post.x)}"
               class="mt-1.5 text-xs text-sky-500 hover:text-sky-700 font-medium transition-colors">
         コピー
       </button>`
    : placeholder;

  return `
<article class="post-card post-card--0${num} bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
  <div class="flex items-stretch">
    <div class="w-1.5 shrink-0 bg-${c}-400" aria-hidden="true"></div>
    <div class="flex-1 p-5">

      <!-- ヘッダー -->
      <div class="flex items-start gap-3 mb-4">
        <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl
                    bg-${c}-100 text-${c}-700 text-sm font-black"
             aria-label="ニュース ${num} の投稿案">
          ${num < 10 ? '0' + num : num}
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-bold text-slate-800">ニュース ${num} の投稿案</p>
          ${post?.emotion ? `<p class="text-xs text-slate-500 mt-0.5">感情軸: ${esc(post.emotion)}</p>` : ''}
        </div>
        <div class="flex items-center gap-2 shrink-0">
          ${post ? weightBadge : ''}
          ${aiBadge}
        </div>
      </div>

      <!-- 本文: Threads | X の2カラム -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

        <!-- Threads -->
        <div class="flex flex-col gap-1">
          <p class="text-xs font-bold text-indigo-600 uppercase tracking-wider flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 192 192" aria-hidden="true">
              <path d="M141.5 85.5c-1.5-8-6.5-15.5-14-20.5-9-6-20.5-7.5-31-4.5-3 1-6 2.5-8.5 4.5-.5-2.5-.5-5-1-7.5H70v82h17.5v-45c1-9 7.5-17 16.5-19 7-1.5 14.5.5 19 6.5 3 4 4 9 4 13.5v44h17.5V89c0-1.5 0-2.5-3-3.5z"/>
            </svg>
            Threads
          </p>
          ${threadsBlock}
        </div>

        <!-- X -->
        <div class="flex flex-col gap-1">
          <p class="text-xs font-bold text-sky-600 uppercase tracking-wider flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.742l7.731-8.843L2.25 2.25h6.856l4.261 5.632 5.877-5.632zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
            </svg>
            X（旧Twitter）
          </p>
          ${xBlock}
        </div>

      </div>
    </div>
  </div>
</article>`;
}

/**
 * @param {Array}  articles  - Top3ニュース
 * @param {string} isoDate   - "YYYY-MM-DD"
 * @param {Array}  posts     - AI生成投稿案 [{news_index, emotion, weight, threads, x}, ...] または null
 */
export function buildReport(articles, isoDate, posts = null) {
  const d        = new Date(isoDate + 'T00:00:00+09:00');
  const dateJa   = d.toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' });
  const weekday  = ['日', '月', '火', '水', '木', '金', '土'][d.getDay()];
  const genTime  = new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' });

  const newsHtml  = articles.map((a, i) => newsCard(i + 1, a)).join('\n');

  // posts は [{news_index, emotion, weight, threads, x}, ...] 形式（ニュース3本分）
  const postsHtml = articles.map((_, i) => {
    const post = posts?.find(p => p.news_index === i + 1) ?? posts?.[i] ?? null;
    return postCard(i + 1, post);
  }).join('\n');

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
  <script>
    function copyText(btn) {
      const text = btn.dataset.text;
      navigator.clipboard.writeText(text).then(() => {
        const orig = btn.textContent;
        btn.textContent = 'コピー完了！';
        btn.classList.add('text-green-600');
        setTimeout(() => { btn.textContent = orig; btn.classList.remove('text-green-600'); }, 1500);
      }).catch(() => {
        const ta = document.createElement('textarea');
        ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
        document.body.appendChild(ta); ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        btn.textContent = 'コピー完了！';
        setTimeout(() => { btn.textContent = 'コピー'; }, 1500);
      });
    }
  </script>
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

    <!-- ── フェーズ表示 ── -->
    <div class="rounded-xl ${posts ? 'bg-green-50 border-green-200' : 'bg-amber-50 border-amber-200'}
                border px-4 py-3 flex items-start gap-3">
      <span class="text-base shrink-0 mt-0.5" aria-hidden="true">${posts ? '✅' : '📌'}</span>
      <p class="text-xs ${posts ? 'text-green-700' : 'text-amber-700'} leading-relaxed">
        ${posts
          ? '<strong>Phase 2 稼働中</strong>：Groq AI（llama-3.3-70b）によるダイ先生スタイル投稿案の自動生成が有効です。<br><strong>Phase 3</strong> でメール送信（URL のみ）を追加予定です。'
          : '<strong>Phase 1 稼働中</strong>：RSS取得・HTML生成・GitHub Pages 公開まで完了。<br><strong>Phase 2</strong>：GitHub Secrets に <code>GROQ_API_KEY</code> を設定すると AI 生成が有効になります。'
        }
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
