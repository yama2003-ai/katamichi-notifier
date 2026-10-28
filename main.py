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

    # --------------------------------------------------
    # 掲載されている空きプラン（台数）をカウント
    # --------------------------------------------------
    # 片道GO!のプラン要素（カード）を取得（サイト構造に合わせて抽出）
    plan_cards = soup.select(".c-card") or soup.select(".plan-item")
    plan_count = len(plan_cards)

    page_text = soup.get_text()
    current_content_hash = hash(page_text)

    # 初回実行時：ハッシュを記憶
    if len(notified_plans) == 0:
      notified_plans.add(current_content_hash)
      print(f"初期状態を記憶しました。（現在の空き台数: {plan_count}台）")
      return

    # 内容の更新を検知した場合
    if current_content_hash not in notified_plans:
      count_info = (
          f"🚗 現在の空き台数: {plan_count}台"
          if plan_count > 0
          : "🚗 空きプランあり（詳細はサイトをご確認ください）"
      )

      message = (
          f"【片道GO！更新通知】\n\n"
          f"新しいプランの追加・更新を検知しました！\n"
          f"{count_info}\n\n"
          f"確認URL:\n{TARGET_URL}"
      )
      send_line_notification(message)
      notified_plans.add(current_content_hash)
      print("更新を検知して通知を送信しました。")
    else:
      print("新しい更新はありませんでした。")

  except Exception as e:
    print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
  check_katamichi_go()
