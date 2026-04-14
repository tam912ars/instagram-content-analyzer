"""
Gmail 送信モジュール

レポートの URL と3行サマリーを指定アドレスへ送信する。

設定（環境変数）:
  GMAIL_USER         送信元 Gmail アドレス
  GMAIL_APP_PASSWORD Gmail アプリパスワード（2段階認証が必要）
  GMAIL_TO           送信先メールアドレス（カンマ区切りで複数指定可）
  GITHUB_PAGES_BASE  GitHub Pages のベースURL
                     例: https://yourname.github.io/instagram-content-analyzer
"""
import logging
import os
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger(__name__)


def _build_report_url(report_date: date) -> str:
    """GitHub Pages 上のレポート URL を組み立てる"""
    base = os.getenv("GITHUB_PAGES_BASE", "").rstrip("/")
    filename = f"reports/{report_date.isoformat()}.html"
    if base:
        return f"{base}/{filename}"
    # ベースURLが未設定の場合はファイルパスのみ返す（ローカルテスト用）
    return filename


def _build_email_html(
    report_url: str,
    report_date: date,
    summary: str,
    top3_titles: list[str],
) -> str:
    """送信するメール本文（HTML）を組み立てる"""
    date_str = report_date.strftime("%Y年%m月%d日（%a）")
    top3_html = "".join(
        f'<li style="margin:6px 0; padding:8px 12px; background:#f0f4ff; '
        f'border-left:3px solid #4f46e5; border-radius:4px; font-size:14px;">'
        f'<strong>#{i}</strong> {title}</li>'
        for i, title in enumerate(top3_titles[:3], 1)
    )
    return f"""<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; background:#f9fafb; font-family: 'Hiragino Sans', sans-serif;">
  <div style="max-width:600px; margin:32px auto; background:#ffffff;
              border-radius:12px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.08);">

    <!-- ヘッダー -->
    <div style="background:linear-gradient(135deg,#1e1b4b,#312e81); padding:28px 32px;">
      <p style="margin:0; color:#a5b4fc; font-size:12px; letter-spacing:2px;">DAILY CONTENT REPORT</p>
      <h1 style="margin:6px 0 0; color:#ffffff; font-size:22px; font-weight:700;">
        📊 ダイ先生 今日のコンテンツ案
      </h1>
      <p style="margin:8px 0 0; color:#c7d2fe; font-size:13px;">{date_str}</p>
    </div>

    <!-- サマリー -->
    <div style="padding:24px 32px 16px;">
      <p style="margin:0 0 4px; font-size:11px; color:#6b7280; letter-spacing:1px; text-transform:uppercase;">
        今日のひとことまとめ
      </p>
      <p style="margin:0; font-size:15px; color:#1f2937; line-height:1.6; font-weight:500;">
        {summary}
      </p>
    </div>

    <!-- TOP3 -->
    <div style="padding:0 32px 24px;">
      <p style="margin:0 0 10px; font-size:11px; color:#6b7280; letter-spacing:1px; text-transform:uppercase;">
        今日いちばん伸びそうなネタ 3選
      </p>
      <ul style="list-style:none; margin:0; padding:0;">
        {top3_html}
      </ul>
    </div>

    <!-- CTA ボタン -->
    <div style="padding:0 32px 32px; text-align:center;">
      <a href="{report_url}"
         style="display:inline-block; padding:14px 36px;
                background:linear-gradient(135deg,#4f46e5,#7c3aed);
                color:#ffffff; text-decoration:none; border-radius:8px;
                font-size:15px; font-weight:700; letter-spacing:0.5px;">
        📋 図解レポートを開く →
      </a>
      <p style="margin:12px 0 0; font-size:11px; color:#9ca3af;">
        {report_url}
      </p>
    </div>

    <!-- フッター -->
    <div style="border-top:1px solid #f3f4f6; padding:16px 32px;
                background:#f9fafb; text-align:center;">
      <p style="margin:0; font-size:11px; color:#9ca3af;">
        ダイ先生 コンテンツ分析ボット ・ 毎朝 6:30 自動配信
      </p>
    </div>
  </div>
</body>
</html>"""


def send_report_email(
    report_date: date,
    summary: str,
    top3_titles: list[str],
    report_url: Optional[str] = None,
) -> bool:
    """
    レポート URL とサマリーを Gmail で送信する。

    Parameters
    ----------
    report_date  : レポートの日付
    summary      : AI が生成した一言サマリー
    top3_titles  : TOP3 ネタのタイトルリスト
    report_url   : レポートの URL（省略時は環境変数から自動生成）

    Returns
    -------
    bool : 送信成功なら True
    """
    gmail_user = os.getenv("GMAIL_USER", "")
    app_password = os.getenv("GMAIL_APP_PASSWORD", "")
    gmail_to_raw = os.getenv("GMAIL_TO", "")

    if not gmail_user or not app_password or not gmail_to_raw:
        logger.error(
            "Gmail 設定が不完全です。GMAIL_USER / GMAIL_APP_PASSWORD / GMAIL_TO を設定してください。"
        )
        return False

    recipients = [addr.strip() for addr in gmail_to_raw.split(",") if addr.strip()]
    if not recipients:
        logger.error("GMAIL_TO が空です。")
        return False

    if report_url is None:
        report_url = _build_report_url(report_date)

    date_str = report_date.strftime("%Y/%m/%d")
    subject = f"📊 [{date_str}] ダイ先生 今日のコンテンツ案レポート"
    html_body = _build_email_html(report_url, report_date, summary, top3_titles)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, app_password)
            server.sendmail(gmail_user, recipients, msg.as_string())
        logger.info("メール送信完了 → %s", ", ".join(recipients))
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error(
            "Gmail 認証エラー。アプリパスワードを確認してください。"
            "（通常のパスワードは使えません）"
        )
        return False
    except Exception as e:
        logger.error("メール送信失敗: %s", e)
        return False
