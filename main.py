import os
import time
from bs4 import BeautifulSoup
import requests

# --------------------------------------------------
# 設定
# --------------------------------------------------
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_TOKEN")
USER_ID = os.environ.get("LINE_USER_ID")
TARGET_URL = "https://cp.toyota.jp/rentacar/?padid=ag270_fr_sptop_onewayma"


def send_line_notification(message):
  url = "https://api.line.me/v2/bot/message/push"
  headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
  }
  payload = {
      "to": USER_ID,
      "messages": [{"type": "text", "text": message}],
  }
  try:
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    print("LINE通知を送信しました。")
  except requests.exceptions.RequestException as e:
    print(f"LINE通知の送信に失敗しました: {e}")


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

    # 安全なif文でテキストを結合
    if plans_detail:
      detail_text = "\n\n".join(plans_detail)
    else:
      detail_text = (
          "詳細なテキストの取得ができませんでしたが、プランが掲載されています。"
      )

    print(f"現在の空き台数: {plan_count}台")

    # --------------------------------------------------
    # 空きプランがある場合、区間や詳細を載せて通知
    # --------------------------------------------------
    if plan_count > 0:
      message = (
          f"🚗【片道GO！空きプラン通知】\n\n"
          f"現在の空き台数: {plan_count}台\n\n"
          f"{detail_text}\n\n"
          f"確認URL:\n{TARGET_URL}"
      )
      send_line_notification(message)
      print("空きプランの区間情報を通知しました。")
    else:
      print("現在、空きプランはありません（通知なし）。")

  except Exception as e:
    print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
  check_katamichi_go()
