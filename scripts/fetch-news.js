/**
 * fetch-news.js
 * RSSフィードからニュースを取得する
 * Phase 1: AI不使用・RSS description をそのまま使用
 */
import Parser from 'rss-parser';

const parser = new Parser({ timeout: 10000 });

// Google News RSS: キーワード指定で教育ニュースに絞り込む
const GN = (q) =>
  `https://news.google.com/rss/search?q=${encodeURIComponent(q)}&hl=ja&gl=JP&ceid=JP:ja`;

const RSS_SOURCES = [
  { name: 'Google News（教員不足）',  url: GN('教員不足 OR 代替教員') },
  { name: 'Google News（教師働き方）', url: GN('教師 働き方 OR 残業 OR 給特法') },
  { name: 'Google News（部活動）',    url: GN('部活動 地域移行 OR 部活 教師') },
  { name: 'NHK News（社会）',         url: 'https://www3.nhk.or.jp/rss/news/cat4.xml' },
];

export async function fetchNews() {
  const results = await Promise.allSettled(
    RSS_SOURCES.map(source => fetchSingle(source))
  );

  const articles = results
    .filter(r => r.status === 'fulfilled')
    .flatMap(r => r.value);

  if (articles.length === 0) {
    console.warn('  ⚠️  全RSSソースの取得に失敗。ダミーデータを使用します。');
    return getDummyNews();
  }

  return articles;
}

async function fetchSingle({ name, url }) {
  try {
    const feed = await parser.parseURL(url);
    console.log(`  ✓ ${name}: ${feed.items.length}件`);
    return feed.items.map(item => ({
      title:       (item.title || '').trim(),
      description: (item.contentSnippet || item.description || '').trim().slice(0, 200),
      url:         item.link || '',
      publishedAt: item.pubDate || '',
      source:      name,
    }));
  } catch (err) {
    console.warn(`  ✗ ${name} 取得失敗: ${err.message}`);
    return [];
  }
}

// RSS が全滅したときのフォールバック用ダミーデータ
function getDummyNews() {
  return [
    {
      title: '全国1000校超で「代替教員なし」産育休でクラス担任が空白に',
      description:
        '産休・育休取得による代替教員の確保が全国で困難になっており、担任不在のまま新年度を迎えた学校が1000校を超えた。教員不足が深刻化するなか、子どもたちへの影響を懸念する声が広がっている。',
      url: '#',
      publishedAt: new Date().toISOString(),
      source: 'ダミーデータ',
    },
    {
      title: '新年度の職員室「名前を覚える前に業務が始まる」新任教員の孤立が深刻',
      description:
        '新年度初日から膨大な業務に直面する新任教員の孤立感を訴えた投稿が拡散。同じ経験を持つ教員たちの共感コメントが殺到し、4月の過酷な現場環境が改めて可視化された。',
      url: '#',
      publishedAt: new Date().toISOString(),
      source: 'ダミーデータ',
    },
    {
      title: '部活動の地域移行、実態は「教師が無償ボランティア」として継続',
      description:
        '部活動の地域移行が進む中、実際には教師がボランティアとして従前と変わらず指導を継続している実態が報告。制度と現場のギャップが改めて浮き彫りとなっている。',
      url: '#',
      publishedAt: new Date().toISOString(),
      source: 'ダミーデータ',
    },
  ];
}
