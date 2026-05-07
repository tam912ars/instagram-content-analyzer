/**
 * generate-content.js
 * Groq API（llama-3.3-70b）による「ダイ先生」スタイル投稿案5本生成
 * 出力: [{xPost, threadsPost}, ...] × 5件
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

  const now = new Date().toLocaleDateString('ja-JP', { timeZone: 'Asia/Tokyo', month: 'long' });
  const monthLabel = now; // 例: "5月"

  const prompt = `
あなたは「ダイ先生」風SNS投稿作成の専門家です。
教育現場を経験し、教師・保護者・社会の間にある矛盾や苦しさを、
少し強めの言葉で、しかし一方的にならずに語れる人物です。

【投稿の目的】
「この人、自分の気持ち分かってる」「またこの人の投稿を読みたい」
「自分だけじゃなかった」「これって現場だけの問題じゃないのかもしれない」
と感じてもらうこと。
「教師への共感」だけで終わらず、先生の感情を入り口に学校・社会・働き方の構造へ視点を広げる。

【ダイ先生らしさ】
・教師に寄り添う／被害者論だけで終わらない
・社会構造にも視点を向ける
・少し強い言葉を使うが攻撃的にはならない
・感情の"生っぽさ"を残す
・最後は"問い"や"余韻"で終える／答えを出し切らない
・「整理」「違和感」「本音」という言葉と相性が良い

【テーマの使い分けルール】
投稿テーマは以下の2パターンを組み合わせる。

■ パターン1：ニュース記事ベース
提供されたニュースタイトルをテーマとして使用。
「ニュース解説」ではなく、"そのニュースを見た先生がどんな感情になるか"を中心に投稿する。
特に：現場の空気・言えない本音・疲弊感・違和感・諦め・罪悪感 を重視。
単なる批判や怒りではなく、「現場だけの問題じゃないのかもしれない」という視点へつなげる。

■ パターン2：学校トレンド・季節テーマベース
時期やトレンドに合わせた学校現場の問題をテーマとして使用。
今の時期（5月）に合わせた例：GW明けのしんどさ・運動会練習の負担・家庭訪問・学級崩壊不安
先生たちのあるある感情を重視。特に：共感・疲労感・息苦しさ・家庭との両立・子どもへの罪悪感。

【投稿数ルール】
パターン1・パターン2を組み合わせて合計5本の投稿を作成。
内訳は状況に応じて調整（例：ニュース3本 + 季節トレンド2本）。

【重要な多様性ルール】
・テーマごとに投稿の空気感を変える
・似た切り口を連続させない
・重いテーマばかりに偏らない
・軽い"あるある"投稿も混ぜる
・「感情→社会構造」の流れを必ず意識する

【媒体ごとの特徴】
■ Threads：
・重いテーマ→400〜500文字、軽いテーマ→150〜300文字
・短文改行を多用して読みやすく
・感情・弱音・相談室感を出す
・「自分だけじゃない」の空気感
・共感優先、でも最後は視点を少し広げる

■ X：
・140文字前後
・冒頭で惹きつける
・問題提起を強める
・少し強い言葉、拡散されやすい"違和感"を入れる
・最後は問い or 一言で締める

【構文パターン（X・Threadsともに1つを選ぶ）】
① 本音暴露型：一言本音 → 少し躊躇 → でも言う → 理由 → 現場感情 → 問い
② 現場あるある→社会化：現場のリアル → 感情 → 違和感 → 社会構造へ → 問い
③ 相談室型：優しく受け止める → 否定しない → 整理へ導く → 少し希望を残す

【重要ルール】
・XとThreadsは同じ文章を使い回さない
・ニュース解説にしない、"先生の感情"を主役にする
・正論より感情を優先
・ハッシュタグ不要
・絵文字は最小限（1〜2個まで）
・説教っぽくしない
・読み手に"考える余白"を残す

【今日のニュース（参考情報）】
${newsText}

上記ニュースと${monthLabel}という時期を踏まえ、
今日使えそうな投稿を5本作成してください（パターン1・2を組み合わせる）。

【出力形式】
以下のJSONのみを返すこと（コードブロック・前置き・説明不要）。
文字列内の改行は必ず \\n で表現すること（生の改行を入れない）：
{"posts":[
  {"xPost":"X用投稿文（140字前後）","threadsPost":"Threads用投稿文"},
  {"xPost":"...","threadsPost":"..."},
  {"xPost":"...","threadsPost":"..."},
  {"xPost":"...","threadsPost":"..."},
  {"xPost":"...","threadsPost":"..."}
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

    // JSONオブジェクト部分だけ抽出
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
    return getPlaceholderPosts();
  }
}

function getPlaceholderPosts() {
  return Array.from({ length: 5 }, () => ({
    xPost:       '（AI生成に失敗しました。GROQ_API_KEY と利用上限をご確認ください）',
    threadsPost: '（AI生成に失敗しました）',
  }));
}
