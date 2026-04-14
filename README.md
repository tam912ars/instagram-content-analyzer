# 📊 ダイ先生 Instagram コンテンツ分析ツール

Instagramの過去の投稿・コメントをAIで分析し、毎日のコンテンツ案（フィード・リール・スタエフ・YouTubeライブ）を図解で提案するツールです。

## 機能

- **ダッシュボード**: エンゲージメント推移・コメントキーワード・ハッシュタグ・投稿タイプ別分析
- **AIコンテンツ提案**: GPT-4o がデータを分析して以下を自動生成
  - 📸 フィード投稿ネタ案（フック・本文・キャプション・ハッシュタグ）
  - 🎬 リールネタ案（構成・BGMムード）
  - 🎙️ スタエフ トークネタ（トーク構成・時間目安）
  - 📺 YouTubeライブ ネタ（アジェンダ・想定Q&A）
- **投稿一覧**: エンゲージメント順の投稿管理

## セットアップ

### 1. 依存パッケージをインストール

```bash
cd instagram-content-analyzer
pip install -r requirements.txt
```

### 2. 環境変数を設定

```bash
cp .env.example .env
```

`.env` を編集してAPIキーを設定:

```env
INSTAGRAM_ACCESS_TOKEN=your_token
INSTAGRAM_ACCOUNT_ID=your_account_id
OPENAI_API_KEY=sk-...
```

### 3. アプリを起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が開きます。

## デモモード

APIキーなしでもデモデータで動作確認できます。
サイドバーの「🔧 デモデータで動作確認」をONにしてください。

## Instagram Graph API の取得方法

1. [Meta Developers](https://developers.facebook.com/) でアプリを作成
2. Instagram Graph API を有効化
3. ビジネスアカウントを連携
4. アクセストークンとアカウントIDを取得

## フォルダ構成

```
instagram-content-analyzer/
├── app.py                        # Streamlit メインアプリ
├── requirements.txt
├── .env.example
├── src/
│   ├── instagram/
│   │   ├── client.py             # Instagram Graph API クライアント
│   │   └── mock_data.py          # デモ用モックデータ
│   ├── analysis/
│   │   └── post_analyzer.py      # 投稿・コメント分析
│   └── ai/
│       └── content_generator.py  # GPT-4o コンテンツ案生成
├── data/cache/                   # APIレスポンスキャッシュ
└── reports/                      # 生成レポート保存先
```
