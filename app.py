"""メインアプリ - ダイ先生 Instagram コンテンツ分析ダッシュボード"""
import os
import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from src.analysis.post_analyzer import (
    extract_hashtags,
    get_comment_keywords,
    get_engagement_trend,
    get_frequently_asked_questions,
    get_post_type_breakdown,
    get_top_posts,
    parse_posts,
)
from src.instagram.mock_data import generate_mock_account, generate_mock_posts
from src.visualization.html_report import generate_html_report
from src.trends.mock_news import get_mock_news, get_mock_x_trends
from src.trends.scorer import get_top3_content_ideas, get_dual_summary, score_news_item

REPORTS_DIR = Path(__file__).parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────
# ページ設定
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ダイ先生 コンテンツ分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# カスタムCSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stMetric { background: #1e2130; border-radius: 12px; padding: 16px; }
    .idea-card {
        background: linear-gradient(135deg, #1e2130 0%, #252840 100%);
        border-left: 4px solid #e040fb;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .reel-card {
        background: linear-gradient(135deg, #1e2130 0%, #252840 100%);
        border-left: 4px solid #ff4081;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .audio-card {
        background: linear-gradient(135deg, #1e2130 0%, #252840 100%);
        border-left: 4px solid #40c4ff;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .yt-card {
        background: linear-gradient(135deg, #1e2130 0%, #252840 100%);
        border-left: 4px solid #ff1744;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .insight-box {
        background: #1a2332;
        border: 1px solid #2d3f5c;
        border-radius: 8px;
        padding: 12px;
        margin: 6px 0;
    }
    h1, h2, h3 { color: #e0e0e0; }
    .report-date { color: #90caf9; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# サイドバー
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://via.placeholder.com/120x120/e040fb/ffffff?text=DAI", width=80)
    st.title("📊 ダイ先生\nコンテンツ分析")
    st.divider()

    use_mock = st.toggle("🔧 デモデータで動作確認", value=True, help="APIキー不要でデモ動作します")
    st.divider()

    st.subheader("⚙️ 設定")
    max_posts = st.slider("分析する投稿数", 10, 50, 20, 5)
    top_n = st.slider("上位表示件数", 3, 10, 5)

    st.divider()
    st.caption("🔑 APIキーは `.env` ファイルに設定してください")

    generate_report = st.button("🤖 AIレポートを生成", type="primary", use_container_width=True)

# ─────────────────────────────────────────────
# データ取得
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_data(use_mock: bool, max_posts: int):
    if use_mock:
        posts = generate_mock_posts(max_posts)
        account = generate_mock_account()
    else:
        from src.instagram.client import InstagramClient
        client = InstagramClient()
        posts = client.get_all_posts_with_comments(max_posts=max_posts)
        account = client.get_account_insights()
    return posts, account

with st.spinner("データ読み込み中..."):
    raw_posts, account = load_data(use_mock, max_posts)

df = parse_posts(raw_posts)
captions = df["caption"].tolist()
comment_keywords = get_comment_keywords(raw_posts, top_n=20)
hashtags = extract_hashtags(captions)
questions = get_frequently_asked_questions(raw_posts)
top_posts_df = get_top_posts(df, n=top_n)
type_breakdown = get_post_type_breakdown(df)
trend_df = get_engagement_trend(df)

# 教育系ニュース・トレンドデータ
news_items = get_mock_news()
x_trends = get_mock_x_trends()
scored_news = [score_news_item(item, comment_keywords, captions) for item in news_items]
scored_news_sorted = sorted(scored_news, key=lambda x: x.get("trend_score", 0), reverse=True)
top3_ideas = get_top3_content_ideas(news_items, comment_keywords, captions)
dual_summary = get_dual_summary(comment_keywords, news_items)

# ─────────────────────────────────────────────
# ヘッダー
# ─────────────────────────────────────────────
col_title, col_date = st.columns([4, 1])
with col_title:
    st.title(f"📊 {account.get('name', 'ダイ先生')} — Instagram コンテンツ分析")
with col_date:
    st.markdown(f"<p class='report-date'>🗓️ {datetime.now().strftime('%Y年%m月%d日 %H:%M')}</p>", unsafe_allow_html=True)
    if use_mock:
        st.caption("🔧 デモデータ")

# ─────────────────────────────────────────────
# KPI メトリクス
# ─────────────────────────────────────────────
st.subheader("📈 アカウント概要")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("フォロワー", f"{account.get('followers_count', 0):,}")
k2.metric("投稿数", f"{account.get('media_count', 0):,}")
k3.metric("分析投稿数", len(df))
k4.metric("平均いいね", f"{df['like_count'].mean():.0f}" if not df.empty else "0")
k5.metric("平均コメント", f"{df['comments_count'].mean():.0f}" if not df.empty else "0")

st.divider()

# ─────────────────────────────────────────────
# ファーストビュー：デュアルサマリー
# ─────────────────────────────────────────────
with st.container():
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown("#### 📊 今フォロワーが反応していること")
        follower_topics = dual_summary.get("follower_topics", [])
        if follower_topics:
            st.markdown(" ".join(f"`{t}`" for t in follower_topics))
        seasonal = dual_summary.get("seasonal_keywords", [])
        if seasonal:
            st.caption(f"🗓️ 旬のキーワード: {' / '.join(seasonal)}")
    with col_f2:
        st.markdown("#### 📰 今外部で話題の教育テーマ")
        for topic in dual_summary.get("external_topics", []):
            st.markdown(f"▸ {topic}")
        top_news = dual_summary.get("top_news_title", "")
        top_score = dual_summary.get("top_news_score", 0)
        if top_news:
            st.warning(f"🔥 最注目: {top_news}（{top_score}pt）")

st.divider()

# ─────────────────────────────────────────────
# タブ構成
# ─────────────────────────────────────────────
tab_dashboard, tab_trends, tab_report, tab_posts = st.tabs([
    "📊 ダッシュボード",
    "📰 外部トレンド・教育ニュース",
    "🤖 AIコンテンツ提案",
    "📋 投稿一覧",
])

# ─────────────────────────────────────── TAB 1: ダッシュボード
with tab_dashboard:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔑 コメントキーワード TOP 20")
        if comment_keywords:
            kw_df = pd.DataFrame(comment_keywords, columns=["キーワード", "出現数"])
            fig = px.bar(
                kw_df,
                x="出現数",
                y="キーワード",
                orientation="h",
                color="出現数",
                color_continuous_scale="Purples",
                height=500,
            )
            fig.update_layout(
                paper_bgcolor="#0e1117",
                plot_bgcolor="#0e1117",
                font_color="#e0e0e0",
                yaxis=dict(autorange="reversed"),
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("キーワードデータなし")

    with col2:
        st.subheader("📸 投稿タイプ別パフォーマンス")
        if type_breakdown:
            type_df = pd.DataFrame(type_breakdown)
            fig2 = px.bar(
                type_df,
                x="media_type",
                y=["avg_likes", "avg_comments"],
                barmode="group",
                labels={"value": "平均数", "media_type": "投稿タイプ", "variable": "指標"},
                color_discrete_map={"avg_likes": "#e040fb", "avg_comments": "#40c4ff"},
                height=400,
            )
            fig2.update_layout(
                paper_bgcolor="#0e1117",
                plot_bgcolor="#1e2130",
                font_color="#e0e0e0",
            )
            st.plotly_chart(fig2, use_container_width=True)

            pie_fig = px.pie(
                type_df,
                names="media_type",
                values="count",
                color_discrete_sequence=["#e040fb", "#40c4ff"],
                hole=0.4,
                height=250,
            )
            pie_fig.update_layout(
                paper_bgcolor="#0e1117",
                font_color="#e0e0e0",
                margin=dict(t=20, b=20),
            )
            st.plotly_chart(pie_fig, use_container_width=True)

    st.subheader("📈 エンゲージメント推移")
    if not trend_df.empty:
        fig3 = px.line(
            trend_df,
            x="date",
            y="avg_engagement",
            markers=True,
            labels={"date": "日付", "avg_engagement": "平均エンゲージメント"},
            color_discrete_sequence=["#e040fb"],
            height=300,
        )
        fig3.update_layout(
            paper_bgcolor="#0e1117",
            plot_bgcolor="#1e2130",
            font_color="#e0e0e0",
        )
        st.plotly_chart(fig3, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("🏷️ よく使うハッシュタグ")
        if hashtags:
            tag_df = pd.DataFrame(hashtags[:15], columns=["ハッシュタグ", "使用数"])
            fig4 = px.treemap(
                tag_df,
                path=["ハッシュタグ"],
                values="使用数",
                color="使用数",
                color_continuous_scale="Purples",
                height=300,
            )
            fig4.update_layout(paper_bgcolor="#0e1117", font_color="#e0e0e0")
            st.plotly_chart(fig4, use_container_width=True)

    with col4:
        st.subheader("❓ よく寄せられる質問")
        if questions:
            for q in questions[:8]:
                st.markdown(f"<div class='insight-box'>💬 {q}</div>", unsafe_allow_html=True)
        else:
            st.info("質問コメントなし")

# ─────────────────────────────────────── TAB 2: 外部トレンド
with tab_trends:
    st.subheader("🏆 今日いちばん伸びそうなネタ 3選")
    st.caption("過去の類似投稿・季節一致・ニュース接続・コメント熱量・外部トレンドの複合スコアで選定")

    _CAUTION_COLOR = {"低": "normal", "中": "off", "高": "inverse"}
    _FORMAT_EMOJI = {"リール": "🎬", "フィード": "📸", "YouTubeライブ": "📺", "スタエフ": "🎙️"}

    for rank, item in enumerate(top3_ideas, 1):
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        with st.expander(f"{medals[rank]} 第{rank}位：{item['title'][:50]}…  【総合 {item.get('composite_score', 0):.0f}pt】", expanded=True):
            col_a, col_b = st.columns([3, 2])
            with col_a:
                bd = item.get("score_breakdown", {})
                score_data = pd.DataFrame({
                    "指標": ["過去の類似投稿", "季節一致度", "ニュース接続", "コメント熱量", "外部トレンド"],
                    "スコア": [bd.get("past_performance", 0), bd.get("seasonal", 0), bd.get("news_connection", 0), bd.get("comment_heat", 0), bd.get("external_trend", 0)],
                })
                fig_radar = px.bar_polar(score_data, r="スコア", theta="指標", color="スコア",
                                          color_continuous_scale="Purples", range_r=[0, 100], height=280)
                fig_radar.update_layout(paper_bgcolor="#0e1117", font_color="#e0e0e0", coloraxis_showscale=False)
                st.plotly_chart(fig_radar, use_container_width=True)
            with col_b:
                st.markdown(f"**✏️ 推奨切り口**\n\n{item.get('angle_memo', '')}")
                fmts = " ".join(_FORMAT_EMOJI.get(f, f) + f" {f}" for f in item.get("formats", []))
                st.markdown(f"**向いている形式:** {fmts}")
                cl = item.get("caution_level", "中")
                icon = {"低": "🟢", "中": "🟡", "高": "🔴"}.get(cl, "🟡")
                st.caption(f"{icon} 取り扱い注意度：{cl}　{item.get('caution_reason', '')}")

    st.divider()
    st.subheader("📰 外部トレンド・教育ニュース一覧")

    # フィルター
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        source_filter = st.multiselect("出典種別", ["教育新聞", "地方新聞", "X"], default=["教育新聞", "地方新聞", "X"])
    with filter_col2:
        caution_filter = st.multiselect("取り扱い注意度", ["低", "中", "高"], default=["低", "中", "高"])
    with filter_col3:
        format_filter = st.multiselect("向いている形式", ["リール", "フィード", "YouTubeライブ", "スタエフ"], default=[])

    filtered_news = [
        item for item in scored_news_sorted
        if item.get("source_type") in source_filter
        and item.get("caution_level") in caution_filter
        and (not format_filter or any(f in item.get("formats", []) for f in format_filter))
    ]

    st.caption(f"{len(filtered_news)} 件表示中")

    _EMOTION_ICON = {"怒り": "😠", "不安": "😰", "共感": "🤝", "驚き": "😲", "悲しみ": "😢", "感動": "😭", "期待": "🌟", "落胆": "😔", "懐疑": "🤔", "疲労感": "😩", "あきらめ": "😞", "温かさ": "🥰"}
    _CONN_STAR = lambda n: "★" * n + "☆" * (5 - n)

    for item in filtered_news:
        source_type = item.get("source_type", "X")
        source_icon = {"教育新聞": "📰", "地方新聞": "🗞️", "X": "🐦"}.get(source_type, "📄")
        caution_level = item.get("caution_level", "中")
        caution_icon = {"低": "🟢", "中": "🟡", "高": "🔴"}.get(caution_level, "🟡")

        with st.expander(
            f"{source_icon} [{source_type}] {item['title'][:55]}…  "
            f"話題度:{item.get('trend_score',0)}pt  接続:{_CONN_STAR(item.get('connection_score',1))}  {caution_icon}",
            expanded=False,
        ):
            col_n1, col_n2 = st.columns([3, 2])
            with col_n1:
                st.markdown(f"**概要:** {item.get('summary', '')}")
                tags = " ".join(f"`{t}`" for t in item.get("genre_tags", []))
                st.markdown(f"**タグ:** {tags}")
                emotions_str = "　".join(
                    f"{_EMOTION_ICON.get(e['type'], '')} {e['type']}({int(e['intensity']*100)}%)"
                    for e in item.get("emotions", [])
                )
                st.markdown(f"**感情傾向:** {emotions_str}")
                fmts = " / ".join(_FORMAT_EMOJI.get(f, f) + f" {f}" for f in item.get("formats", []))
                st.markdown(f"**向いている形式:** {fmts}")
                if item.get("x_rt_count"):
                    st.caption(f"🐦 X: 🔁{item['x_rt_count']:,}RT  ❤️{item.get('x_like_count', 0):,}いいね")
            with col_n2:
                st.info(f"✏️ **切り口メモ**\n\n{item.get('angle_memo', '')}")
                st.warning(f"{caution_icon} 注意度：{caution_level}\n\n{item.get('caution_reason', '')}")

    st.divider()
    st.subheader("🐦 X トレンドキーワード")
    x_df = pd.DataFrame(x_trends)
    if not x_df.empty:
        fig_x = px.bar(
            x_df.sort_values("tweet_count", ascending=True),
            x="tweet_count", y="keyword", orientation="h",
            color="tweet_count", color_continuous_scale="Blues",
            labels={"tweet_count": "ツイート数", "keyword": "キーワード"},
            height=350,
        )
        fig_x.update_layout(paper_bgcolor="#0e1117", plot_bgcolor="#0e1117", font_color="#e0e0e0", coloraxis_showscale=False)
        st.plotly_chart(fig_x, use_container_width=True)


# ─────────────────────────────────────── TAB 3: AIレポート
with tab_report:
    if "report" not in st.session_state:
        st.session_state.report = None
    if "report_html" not in st.session_state:
        st.session_state.report_html = None
    if "report_filename" not in st.session_state:
        st.session_state.report_filename = None

    if generate_report:
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if not openai_key or openai_key == "your_openai_api_key_here":
            st.error("⚠️ OpenAI APIキーが設定されていません。`.env` ファイルに `OPENAI_API_KEY` を設定してください。")
        else:
            with st.spinner("🤖 GPT-4o がコンテンツ案を生成中... (20〜40秒ほどかかります)"):
                from src.ai.content_generator import ContentGenerator
                gen = ContentGenerator()
                top_posts_list = top_posts_df.to_dict(orient="records")
                report_data = gen.generate_daily_report(
                    top_posts=top_posts_list,
                    comment_keywords=comment_keywords,
                    questions=questions,
                    hashtags=hashtags,
                )
                st.session_state.report = report_data

                if "error" not in report_data:
                    kpi = {
                        "followers_count": account.get("followers_count", 0),
                        "media_count": account.get("media_count", 0),
                        "avg_likes": df["like_count"].mean() if not df.empty else 0,
                        "avg_comments": df["comments_count"].mean() if not df.empty else 0,
                    }
                    html_str = generate_html_report(
                        report=report_data,
                        account_name=account.get("name", "ダイ先生"),
                        kpi=kpi,
                        news_items=scored_news_sorted,
                        top3_ideas=top3_ideas,
                        dual_summary=dual_summary,
                    )
                    st.session_state.report_html = html_str
                    fname = f"report_{date.today().strftime('%Y%m%d')}.html"
                    st.session_state.report_filename = fname
                    save_path = REPORTS_DIR / fname
                    save_path.write_text(html_str, encoding="utf-8")

    report = st.session_state.report
    report_html = st.session_state.report_html

    if report is None:
        st.info("👈 サイドバーの「AIレポートを生成」ボタンを押してコンテンツ案を作成してください。\n\n※ OpenAI APIキーが必要です。")
        st.markdown("""
**生成されるレポートの内容：**
- 📱 **Instagram投稿ネタ案** × 3件（フィード/リール推奨付き・フック・本文・キャプション・ハッシュタグ）
- 🎙️ **スタエフトークネタ** × 2件（タイトル・トーク構成・時間目安）
- 📺 **YouTubeライブネタ** × 1件（タイトル・アジェンダ・想定Q&A）
- 💡 **データインサイト**（コメントトレンドからの気づき）
        """)

    elif "error" in report:
        st.error(f"生成エラー: {report.get('error')}")
        st.code(report.get("raw", ""))

    else:
        col_ok, col_dl = st.columns([3, 1])
        with col_ok:
            st.success(f"✅ レポート生成完了 — {report.get('date', date.today())}")
        with col_dl:
            if report_html and st.session_state.report_filename:
                st.download_button(
                    label="📥 HTMLをダウンロード",
                    data=report_html.encode("utf-8"),
                    file_name=st.session_state.report_filename,
                    mime="text/html",
                    use_container_width=True,
                )

        components.html(report_html, height=2800, scrolling=True)

# ─────────────────────────────────────── TAB 3: 投稿一覧
with tab_posts:
    st.subheader(f"📋 投稿一覧（全 {len(df)} 件）")

    if not df.empty:
        st.subheader(f"🏆 エンゲージメント上位 {top_n} 件")
        display_df = top_posts_df.copy()
        display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y/%m/%d")
        display_df.columns = ["キャプション", "タイプ", "いいね", "コメント", "エンゲージメント", "投稿日"]
        display_df["キャプション"] = display_df["キャプション"].str[:60] + "..."
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("📋 全投稿")
        all_display = df[["caption", "media_type", "like_count", "comments_count", "engagement", "timestamp"]].copy()
        all_display["timestamp"] = all_display["timestamp"].dt.strftime("%Y/%m/%d")
        all_display.columns = ["キャプション", "タイプ", "いいね", "コメント", "エンゲージメント", "投稿日"]
        all_display["キャプション"] = all_display["キャプション"].str[:60] + "..."
        st.dataframe(all_display, use_container_width=True, hide_index=True)
