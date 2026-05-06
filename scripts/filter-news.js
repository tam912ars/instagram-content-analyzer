/**
 * filter-news.js
 * 教育テーマのキーワードスコアリングでTop N件を選定する
 * ターゲット: 教員（教師視点のニュースを優先）
 * カテゴリ分散: 同じカテゴリから最大1本のみ選定
 */

// カテゴリ別キーワード定義（教員ターゲット）
const KEYWORD_RULES = [
  // ── 働き方・雇用 ──────────────────────────────────────
  { words: ['教員不足', '代替教員', '教師不足'],             score: 10, category: '働き方' },
  { words: ['給特法', '残業代', '時間外労働', '過労'],        score: 9,  category: '働き方' },
  { words: ['離職', '退職', 'バーンアウト', '疲弊'],          score: 8,  category: '働き方' },
  { words: ['産休', '育休', '産育休'],                       score: 7,  category: '働き方' },
  { words: ['採用', '初任', '新任', '教員採用試験'],          score: 6,  category: '働き方' },
  { words: ['働き方改革', '業務削減', '負担軽減'],            score: 7,  category: '働き方' },

  // ── 部活動 ───────────────────────────────────────────
  { words: ['部活', '部活動', '地域移行', '部活指導'],        score: 9,  category: '部活動' },

  // ── 学校DX・ICT ─────────────────────────────────────
  { words: ['ICT', 'DX', 'GIGAスクール', 'タブレット'],      score: 7,  category: 'ICT' },
  { words: ['AI', '生成AI', 'ChatGPT', 'EdTech'],           score: 7,  category: 'ICT' },
  { words: ['プログラミング教育', 'デジタル教科書'],          score: 6,  category: 'ICT' },

  // ── 特別支援・インクルーシブ ──────────────────────────
  { words: ['特別支援', '特別支援学校', '特別支援学級'],      score: 7,  category: '特別支援' },
  { words: ['発達障害', 'ADHD', '自閉症', 'インクルーシブ'],  score: 7,  category: '特別支援' },
  { words: ['合理的配慮', '通級'],                           score: 6,  category: '特別支援' },

  // ── 保護者対応（教師視点） ────────────────────────────
  { words: ['保護者対応', 'クレーム', '保護者トラブル'],      score: 7,  category: '保護者対応' },

  // ── 職場環境・メンタル ────────────────────────────────
  { words: ['ハラスメント', 'パワハラ', '職場環境'],          score: 7,  category: 'メンタル' },
  { words: ['メンタル', '精神疾患', '休職', 'うつ'],         score: 7,  category: 'メンタル' },

  // ── 制度・政策 ────────────────────────────────────────
  { words: ['文科省', '教育委員会', '学習指導要領'],          score: 5,  category: '制度' },
  { words: ['教育改革', '義務教育', '少人数学級'],            score: 5,  category: '制度' },

  // ── 基本マッチ（カテゴリなし・補助点） ──────────────
  { words: ['教師', '先生', '教員'],                         score: 3,  category: null },
  { words: ['学校', '教育', '授業', '学級'],                  score: 2,  category: null },
];

// 保護者・生徒向けコンテンツを除外するネガティブキーワード
const NEGATIVE_WORDS = [
  '受験', '塾', '模試', '偏差値', '大学入試', '共通テスト',
  '奨学金', '入学式', '卒業式',
];

function scoreArticle(article) {
  const text = `${article.title} ${article.description}`;

  // ネガティブキーワードが含まれる記事は大幅減点
  if (NEGATIVE_WORDS.some(w => text.includes(w))) return -1;

  let total = 0;
  let category = null;
  for (const rule of KEYWORD_RULES) {
    if (rule.words.some(w => text.includes(w))) {
      total += rule.score;
      if (rule.category && !category) category = rule.category;  // 最初にマッチしたカテゴリを採用
    }
  }
  return { score: total, category };
}

const DAYS_LIMIT = 30; // 何日以内の記事を対象とするか

function isRecent(publishedAt) {
  if (!publishedAt) return false; // 日付不明は除外
  const published = new Date(publishedAt);
  if (isNaN(published.getTime())) return false; // パース失敗も除外
  const diffDays = (Date.now() - published.getTime()) / (1000 * 60 * 60 * 24);
  return diffDays <= DAYS_LIMIT;
}

export function filterNews(articles, topN = 3) {
  // スコアリング + 日付フィルタ
  const scored = articles
    .map(article => {
      if (!isRecent(article.publishedAt)) return null; // 30日超は除外
      const result = scoreArticle(article);
      if (result === -1) return null;
      return { ...article, score: result.score, category: result.category };
    })
    .filter(Boolean)
    .sort((a, b) => b.score - a.score);

  // タイトル重複排除
  const seen = new Set();
  const deduped = scored.filter(article => {
    const key = article.title.slice(0, 40).trim();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  // カテゴリ分散: 各カテゴリから最大1本
  const usedCategories = new Set();
  const selected = [];

  // Pass 1: カテゴリありの記事を優先（各カテゴリ1本まで）
  for (const article of deduped) {
    if (selected.length >= topN) break;
    if (article.category && usedCategories.has(article.category)) continue;
    if (article.category) usedCategories.add(article.category);
    selected.push(article);
  }

  // Pass 2: まだ足りなければカテゴリ重複を許容して補充
  if (selected.length < topN) {
    for (const article of deduped) {
      if (selected.length >= topN) break;
      if (selected.includes(article)) continue;
      selected.push(article);
    }
  }

  return selected;
}
