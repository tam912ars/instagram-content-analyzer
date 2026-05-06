/**
 * generate-report.js
 * メインエントリーポイント（オーケストレータ）
 *
 * Phase 1: RSS取得 → キーワード選定 → HTML生成 → ファイル保存
 * Phase 2: Gemini AI 要約・投稿案生成を追加予定
 * Phase 3: メール送信を追加予定
 *
 * 実行方法:
 *   node scripts/generate-report.js            # 通常実行
 *   node scripts/generate-report.js --dry-run  # ファイル保存せず確認のみ
 */

import { mkdirSync, writeFileSync } from 'fs';
import path from 'path';
import { fetchNews }        from './fetch-news.js';
import { filterNews }       from './filter-news.js';
import { buildReport }      from './build-report.js';
import { generatePosts } from './generate-content.js';

const USE_AI = Boolean(process.env.GROQ_API_KEY);

// JST で今日の日付を取得（YYYY-MM-DD）
const today = new Date().toLocaleDateString('sv-SE', { timeZone: 'Asia/Tokyo' });

const isDryRun = process.argv.includes('--dry-run');

async function main() {
  console.log(`\n=== 毎朝自動レポート生成 [${today}] ===`);
  // GEMINI_API_KEY の検出状況を出力（値は非表示）
  const keyLen = (process.env.GROQ_API_KEY ?? '').length;
  console.log(`GROQ_API_KEY: ${keyLen > 0 ? `検出済み（${keyLen}文字）` : '⚠️ 未設定または空'}`);
  console.log(`モード: ${USE_AI ? '🤖 AI あり（Phase 2）' : '📄 AI なし（Phase 1）'}`);
  if (isDryRun) console.log('【ドライランモード】ファイルは保存されません\n');

  // ── Step 1: ニュース取得 ───────────────────────────────────
  console.log('[Step 1] RSS ニュース取得');
  const rawNews = await fetchNews();
  console.log(`  → ${rawNews.length}件 取得`);

  // ── Step 2: キーワードスコアリング → Top3 選定 ─────────────
  console.log('[Step 2] ニュース選定（Top 3）');
  const top3 = filterNews(rawNews, 3);
  console.log(`  → ${top3.length}件 選定`);
  top3.forEach((a, i) => console.log(`  ${i + 1}. [score:${a.score}] ${a.title.slice(0, 40)}…`));

  // ── Step 3: AI 投稿案生成（GEMINI_API_KEY がある場合のみ）──────
  let posts = null;

  if (USE_AI) {
    console.log('[Step 3] Gemini AI: 投稿案5本生成');
    posts = await generatePosts(top3);
    console.log(`  → ${posts.length}本 生成`);
  } else {
    console.log('[Step 3] スキップ（GEMINI_API_KEY 未設定 → Phase 1 モード）');
  }

  // ── Step 4: HTML レポート生成 ──────────────────────────────
  console.log('[Step 4] HTML レポート生成');
  const html = buildReport(top3, today, posts);
  console.log(`  → ${html.length.toLocaleString()} 文字`);

  // ── Step 5: ファイル保存 ───────────────────────────────────
  if (isDryRun) {
    console.log('[Step 5] スキップ（ドライラン）');
  } else {
    console.log('[Step 5] ファイル保存');
    const REPORTS_DIR = 'reports';
    mkdirSync(REPORTS_DIR, { recursive: true });

    const outputPath = path.join(REPORTS_DIR, `${today}.html`);
    writeFileSync(outputPath, html, 'utf8');
    console.log(`  → 保存: ${outputPath}`);
  }

  // ── Step 6: メール送信（Phase 3 で実装予定）───────────────
  console.log('[Step 6] メール送信 … Phase 3 で実装予定');

  console.log(`\n=== 完了 [${today}] ===\n`);
}

main().catch(err => {
  console.error('\n❌ エラーが発生しました:', err.message);
  process.exit(1);
});
