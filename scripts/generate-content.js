/**
 * generate-content.js
 * Groq API による X/Threads 投稿案5本の生成
 * 無料枠: 14,400 req/day, 30 RPM
 * モデル: llama-3.3-70b-versatile（日本語対応）
 */

import Groq from 'groq-sdk';

const MODEL   = process.env.GROQ_MODEL ?? 'llama-3.3-70b-versatile';
const API_KEY = process.env.GROQ_API_KEY ?? '';

function getClient() {
  if (!API_KEY) throw new Error('GROQ_API_KEY が設定されていません');
  return new Groq({ apiKey: API_KEY });
}

/**
 * Top3ニュースをもとにX/Threads投稿案を5本生成
 */
export async function generatePosts(newsItems) {
  const groq = getClient();

  const newsText = newsItems
    .map((n, i) => `【ニュース${i + 1}】\nタイトル: ${n.title}`)
    .join('\n\n');

  const prompt = `
あなたはSNS発信の専門家です。
教育系インフルエンサー「ダイ先生」（現役教員パパ・@dy.papa_teacher）の
X（旧Twitter）/ Threads 向けに投稿案を5本作成してください。

【ダイ先生のキャラクター】
- 現役の小学校教員パパ
- 教師の働き方・教員不足・保護者対応などをリアルに発信
- フォロワーは教師・保護者・教育に関心ある人
- 共感・問い・行動促進を意識した投稿が得意

【参考ニュース】
${newsText}

【投稿ルール】
- 各投稿は140字以内
- 改行を使い読みやすく
- ハッシュタグは1〜2個まで
- 絵文字は適度に使う

【必ず以下のJSON形式のみを返すこと（コードブロック・前置き不要）】
{"posts":[
  {"type":"ニュース×当事者感情×問い","content":"..."},
  {"type":"教師の働き方への問題提起","content":"..."},
  {"type":"現場教師への共感ポスト","content":"..."},
  {"type":"社会への問いを投げるポスト","content":"..."},
  {"type":"LINE導線・相談導線につなげるポスト","content":"..."}
]}
`.trim();

  try {
    const completion = await groq.chat.completions.create({
      model:    MODEL,
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.7,
    });

    const text    = completion.choices[0].message.content.trim();
    const cleaned = text.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '').trim();
    const parsed  = JSON.parse(cleaned);
    return parsed.posts;
  } catch (err) {
    console.warn(`  ⚠️  投稿案生成失敗: ${err.message}`);
    return getPlaceholderPosts();
  }
}

function getPlaceholderPosts() {
  return [
    { type: 'ニュース×当事者感情×問い',         content: '（AI生成に失敗しました。GROQ_API_KEYと利用上限をご確認ください）' },
    { type: '教師の働き方への問題提起',           content: '（AI生成に失敗しました）' },
    { type: '現場教師への共感ポスト',             content: '（AI生成に失敗しました）' },
    { type: '社会への問いを投げるポスト',         content: '（AI生成に失敗しました）' },
    { type: 'LINE導線・相談導線につなげるポスト', content: '（AI生成に失敗しました）' },
  ];
}
