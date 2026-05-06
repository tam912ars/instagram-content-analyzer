/**
 * generate-content.js
 * Gemini AI による記事要約 + X/Threads 投稿案5本の生成
 * Phase 2: @google/generative-ai 使用
 *
 * 環境変数:
 *   GEMINI_API_KEY  - Gemini API キー（必須）
 *   GEMINI_MODEL    - モデル名（省略時: gemini-2.0-flash）
 */

import { GoogleGenerativeAI } from '@google/generative-ai';

const MODEL  = process.env.GEMINI_MODEL ?? 'gemini-1.5-flash';
const API_KEY = process.env.GEMINI_API_KEY ?? '';

// レート制限対策: 呼び出し間に待機（ms）
const CALL_DELAY_MS = 4000;

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

function getModel() {
  if (!API_KEY) throw new Error('GEMINI_API_KEY が設定されていません');
  const genAI = new GoogleGenerativeAI(API_KEY);
  return genAI.getGenerativeModel({ model: MODEL });
}

/**
 * 記事1本の解説要約を生成（500字程度）
 */
export async function summarizeArticle(title, description) {
  const model = getModel();
  const prompt = `
あなたは教育ジャーナリストです。
以下の教育ニュースについて、現役教員・保護者・教育関係者が読んで「背景・課題・影響」を理解できるよう、
500字程度で解説してください。

【解説に含めること】
- ニュースの背景・経緯
- 現場（教師・学校）への具体的な影響
- なぜこの問題が起きているのか
- 今後の課題や注目ポイント

【出力ルール】
- 解説文のみを返す（見出し・箇条書き・前置き不要）
- 500字程度（400〜600字の範囲）
- わかりやすい日本語で書く

タイトル: ${title}
参考情報: ${description}
`.trim();

  try {
    const result = await model.generateContent(prompt);
    return result.response.text().trim().slice(0, 700);
  } catch (err) {
    console.warn(`  ⚠️  要約失敗（${title.slice(0, 20)}…）: ${err.message}`);
    return description || title;
  }
}

/**
 * Top3ニュースをもとにX/Threads投稿案を5本生成
 */
export async function generatePosts(newsItems) {
  const model = getModel();

  const newsText = newsItems
    .map((n, i) => `【ニュース${i + 1}】\nタイトル: ${n.title}\n概要: ${n.summary ?? n.description}`)
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
    const result = await model.generateContent(prompt);
    const text = result.response.text().trim();

    // JSONブロック（```json ... ```）が含まれる場合は除去
    const cleaned = text.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '').trim();
    const parsed  = JSON.parse(cleaned);
    return parsed.posts;
  } catch (err) {
    console.warn(`  ⚠️  投稿案生成失敗: ${err.message}`);
    return getPlaceholderPosts();  // フォールバック
  }
}

/**
 * API失敗時のフォールバック
 */
function getPlaceholderPosts() {
  return [
    { type: 'ニュース×当事者感情×問い',     content: '（AI生成に失敗しました。APIキーと利用上限をご確認ください）' },
    { type: '教師の働き方への問題提起',       content: '（AI生成に失敗しました）' },
    { type: '現場教師への共感ポスト',         content: '（AI生成に失敗しました）' },
    { type: '社会への問いを投げるポスト',     content: '（AI生成に失敗しました）' },
    { type: 'LINE導線・相談導線につなげるポスト', content: '（AI生成に失敗しました）' },
  ];
}

/**
 * ニュース3本の要約を順番に生成（レート制限を考慮して直列実行）
 */
export async function summarizeAll(articles) {
  const results = [];
  for (let i = 0; i < articles.length; i++) {
    console.log(`  要約中 (${i + 1}/${articles.length}): ${articles[i].title.slice(0, 30)}…`);
    const summary = await summarizeArticle(articles[i].title, articles[i].description);
    results.push({ ...articles[i], summary });
    if (i < articles.length - 1) await sleep(CALL_DELAY_MS);
  }
  return results;
}
