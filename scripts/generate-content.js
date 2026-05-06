/**
 * generate-content.js
 * Groq API（llama-3.3-70b）による「ダイ先生」スタイル投稿案生成
 * ニュース3本 × (Threads投稿 + X投稿) = 3セット出力
 */

import Groq from 'groq-sdk';

const MODEL   = process.env.GROQ_MODEL ?? 'llama-3.3-70b-versatile';
const API_KEY = process.env.GROQ_API_KEY ?? '';

function getClient() {
  if (!API_KEY) throw new Error('GROQ_API_KEY が設定されていません');
  return new Groq({ apiKey: API_KEY });
}

export async function generatePosts(newsItems) {
  const groq = getClient();

  const newsText = newsItems
    .map((n, i) => `【ニュース${i + 1}】${n.title}`)
    .join('\n');

  const prompt = `
あなたは「ダイ先生」風SNS投稿作成の専門家です。
教育現場を経験し、教師・保護者・社会の間にある矛盾や苦しさを、
少し強めの言葉で、しかし一方的にならずに語れる人物です。

【投稿の目的】
「この人、自分の気持ち分かってる」「自分だけじゃなかった」
「これって現場だけの問題じゃないのかもしれない」と感じてもらうこと。
「教師への共感」だけで終わらず、先生の感情を入り口に学校・社会・働き方の構造へ視点を広げる。

【ダイ先生らしさ】
・教師に寄り添う／被害者論だけで終わらない
・社会構造にも視点を向ける
・少し強い言葉を使うが攻撃的にはならない
・感情の"生っぽさ"を残す
・最後は"問い"や"余韻"で終える／答えを出し切らない
・「整理」「違和感」「本音」という言葉と相性が良い

【媒体ごとの特徴】
■ Threads：感情・弱音・相談室感。短文改行多用。共感優先。「自分だけじゃない」の空気感。
■ X：問題提起を強める。冒頭で惹きつける。少し強い言葉。拡散されやすい"違和感"。短く鋭く。

【テーマの重さ判定】
軽い（あるある・日常・小さな違和感）→ Threads 150〜300文字
重い（メンタル・教員不足・保護者問題・部活・退職・長時間労働）→ Threads 400〜500文字

【構文パターン（どれか1つを選ぶ）】
① 本音暴露型：一言本音 → 少し躊躇 → でも言う → 理由 → 現場感情 → 問い
② 現場あるある→社会化：現場のリアル → 感情 → 違和感 → 社会構造へ → 問い
③ 相談室型：優しく受け止める → 否定しない → 整理へ導く → 少し希望を残す

【重要ルール】
・媒体ごとに同じ文章を使い回さない
・ニュース解説アカウントにしない
・"先生の感情"を主役にする
・ハッシュタグ不要
・絵文字は最小限（1〜2個まで）
・説教っぽくしない
・読み手に"考える余白"を残す

【対象ニュース】
${newsText}

【出力形式】
以下のJSONのみを返すこと（コードブロック・前置き・説明不要）。
文字列内の改行は必ず \\n（バックスラッシュ+n）で表現すること（生の改行を入れない）：
{"posts":[
  {
    "news_index":1,
    "emotion":"先生が感じやすい感情（例：疲弊感・無力感）",
    "weight":"重い or 軽い",
    "threads":"Threads投稿文（重い→400〜500字、軽い→150〜300字、改行あり）",
    "x":"X投稿文（140字前後、問題提起・違和感・問いで締める）"
  },
  {
    "news_index":2,
    "emotion":"...",
    "weight":"...",
    "threads":"...",
    "x":"..."
  },
  {
    "news_index":3,
    "emotion":"...",
    "weight":"...",
    "threads":"...",
    "x":"..."
  }
]}
`.trim();

  try {
    const completion = await groq.chat.completions.create({
      model:       MODEL,
      messages:    [{ role: 'user', content: prompt }],
      temperature: 0.8,
    });

    const text = completion.choices[0].message.content.trim();

    // コードブロック除去
    let cleaned = text.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '').trim();

    // JSONオブジェクト部分だけ抽出（前後の余分なテキストを除去）
    const jsonMatch = cleaned.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error('JSON オブジェクトが見つかりません');
    cleaned = jsonMatch[0];

    // JSON文字列値内の生の改行をエスケープ（LLMがよく混入させる）
    cleaned = cleaned.replace(/"((?:[^"\\]|\\.)*)"/g, (match, inner) => {
      const fixed = inner
        .replace(/\n/g, '\\n')
        .replace(/\r/g, '\\r')
        .replace(/\t/g, '\\t');
      return `"${fixed}"`;
    });

    const parsed = JSON.parse(cleaned);
    return parsed.posts;
  } catch (err) {
    console.warn(`  ⚠️  投稿案生成失敗: ${err.message}`);
    return getPlaceholderPosts(newsItems.length);
  }
}

function getPlaceholderPosts(count = 3) {
  return Array.from({ length: count }, (_, i) => ({
    news_index: i + 1,
    emotion:    '（生成失敗）',
    weight:     '重い',
    threads:    '（AI生成に失敗しました。GROQ_API_KEY と利用上限をご確認ください）',
    x:          '（AI生成に失敗しました）',
  }));
}
