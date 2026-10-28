import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import requests

# --------------------------------------------------
# 設定
# --------------------------------------------------
MAIL_USER = os.environ.get("MAIL_USER")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_TO = os.environ.get("MAIL_TO")
TARGET_URL = "https://cp.toyota.jp/rentacar/?padid=ag270_fr_sptop_onewayma"


def send_email_notification(subject, message):
  try:
    msg = MIMEText(message, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = MAIL_USER
    msg["To"] = MAIL_TO

    # GmailのSMTPサーバー経由で送信
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(MAIL_USER, MAIL_PASSWORD)
    server.sendmail(MAIL_USER, [MAIL_TO], msg.as_string())
    server.quit()
    print("メール通知を送信しました。")
  except Exception as e:
    print(f"メール通知の送信に失敗しました: {e}")


def check_katamichi_go():
  try:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }
    response = requests.get(TARGET_URL, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # --------------------------------------------------
    # 掲載されているプラン（カード）と区間情報を取得
    # --------------------------------------------------
    plan_cards = soup.select(".c-card") or soup.select(".plan-item")
    plan_count = len(plan_cards)

    plans_detail = []
    if plan_cards:
      for i, card in enumerate(plan_cards, 1):
        card_text = " ".join(card.get_text().split())
        plans_detail.append(f"【プラン {i}】\n{card_text}")

    if plans_detail:
      detail_text = "\n\n".join(plans_detail)
    else:
      detail_text = (
          "詳細なテキストの取得ができませんでしたが、プランが掲載されています。"
      )

    print(f"現在の空き台数: {plan_count}台")

    # --------------------------------------------------
    # 空きプランがある場合、メールで通知
    # --------------------------------------------------
    if plan_count > 0:
      subject = f"【片道GO！】空きプラン検知（現在 {plan_count}台）"
      message = (
          f"片道GO！に空きプランが掲載されています。\n\n"
          f"現在の空き台数: {plan_count}台\n\n"
          f"{detail_text}\n\n"
          f"確認URL:\n{TARGET_URL}"
      )
      send_email_notification(subject, message)
      print("空きプランのメール通知を送信しました。")
    else:
      print("現在、空きプランはありません（通知なし）。")

  except Exception as e:
    print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
  check_katamichi_go()
