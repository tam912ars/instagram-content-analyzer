/**
 * filter-news.js
 * 教育テーマのキーワードスコアリングでTop N件を選定する
 * Phase 1: AI不使用・キーワードマッチのみ
 */

// キーワードとスコアのウェイト定義
const KEYWORD_RULES = [
  { words: ['教員不足', '代替教員', '教師不足'],          score: 10 },
  { words: ['給特法', '残業代', '時間外労働'],            score: 9  },
  { words: ['部活', '部活動', '地域移行'],                score: 8  },
  { words: ['保護者対応', 'モンスター', '保護者'],        score: 7  },
  { words: ['働き方', '働き方改革', '業務削減'],          score: 7  },
  { words: ['離職', '退職', 'バーンアウト', '疲弊'],      score: 7  },
  { words: ['産休', '育休', 'マタハラ'],                  score: 7  },
  { words: ['不登校', 'いじめ', '特別支援'],              score: 6  },
  { words: ['新任', '若手', '初任', '採用'],              score: 6  },
  { words: ['教師', '先生', '教員'],                      score: 4  },
  { words: ['学校', '教育', '授業', '学級'],              score: 3  },
];

function scoreArticle(article) {
  const text = `${article.title} ${article.description}`;
  let total = 0;
  for (const { words, score } of KEYWORD_RULES) {
    if (words.some(w => text.includes(w))) {
      total += score;
    }
  }
  return total;
}

export function filterNews(articles, topN = 3) {
  const seen = new Set();
  return articles
    .map(article => ({ ...article, score: scoreArticle(article) }))
    .sort((a, b) => b.score - a.score)
    .filter(article => {
      // タイトル先頭40字で重複チェック
      const key = article.title.slice(0, 40).trim();
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    })
    .slice(0, topN);
}
