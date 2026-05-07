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

【X投稿のルール】
・140文字前後
・冒頭で惹きつける
・問題提起を強める
・少し強い言葉、拡散されやすい"違和感"を入れる
・最後は問い or 一言で締める
・ハッシュタグ不要
・絵文字は最小限（1〜2個まで）

【Threads投稿のルール】
・重いテーマ→400〜500文字、軽いテーマ→150〜300文字
・短文改行を多用して読みやすく
・感情・弱音・相談室感を出す
・「自分だけじゃない」の空気感
・共感を優先、でも最後は視点を少し広げる
・ハッシュタグ不要
・絵文字は最小限

【構文パターン（X・Threadsともに）】
以下のいずれかを使う：
① 本音暴露型：一言本音 → 少し躊躇 → でも言う → 理由 → 現場感情 → 問い
② 現場あるある→社会化：現場のリアル → 感情 → 違和感 → 社会構造へ → 問い
③ 相談室型：優しく受け止める → 否定しない → 整理へ導く → 少し希望を残す

【重要ルール】
・XとThreadsは同じ文章を使い回さない
・ニュース解説にしない、"先生の感情"を主役にする
・正論より感情を優先
・説教っぽくしない
・読み手に"考える余白"を残す

【今日のニュース（参考情報）】
${newsText}

上記ニュースを踏まえ、今日使えそうな投稿を5本作成してください。
1本ごとにXとThreadsの両方を生成します。
ニュースと投稿を1対1で対応させる必要はありません。
ニュース全体のテーマ・空気感をもとに、今日らしい投稿を5本選んでください。

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
