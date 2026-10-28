import os
import time
from bs4 import BeautifulSoup
import requests

# --------------------------------------------------
# 変更点：GitHub Secretsから安全に読み込む
# --------------------------------------------------
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_TOKEN")
USER_ID = os.environ.get("LINE_USER_ID")
TARGET_URL = "https://cp.toyota.jp/rentacar/?padid=ag270_fr_sptop_onewayma"

TARGET_PREFS = ["東京都", "神奈川県", "千葉県"]
notified_plans = set()


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
  global notified_plans
  try:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }
    response = requests.get(TARGET_URL, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    page_text = soup.get_text()

    found_prefs = [pref for pref in TARGET_PREFS if pref in page_text]

    if found_prefs:
      current_content_hash = hash(page_text)
      if current_content_hash not in notified_plans:
        if len(notified_plans) > 0:
          message = (
              f"【片道GO！更新通知】\n\n"
              f"東京都・神奈川県・千葉県に関連するプランの更新を検知しました！\n\n"
              f"確認URL:\n{TARGET_URL}"
          )
          send_line_notification(message)
        notified_plans.add(current_content_hash)
        print("更新を検知しました。")
    else:
      print("条件に合うエリアのプランは見つかりませんでした。")

  except Exception as e:
    print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
  # GitHub Actionsでは1回実行されて終了するため、whileループは不要になります
  check_katamichi_go()
