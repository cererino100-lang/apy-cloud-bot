
import requests
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD = 13.0

API_URL = "https://app.exponent.finance/api/v1/farms/overview"

def get_apy():
    try:
        r = requests.get(API_URL, timeout=10)
        data = r.json()

        for farm in data["data"]:
            if "YT-eUSX" in farm["symbol"]:
                return farm["ytImpliedRateAnnualizedPct"] * 100
        return None
    except Exception as e:
        print("Errore:", e)
        return None

def send_alert(apy):
    msg = f"⚠️ APY sotto soglia!\nValore attuale: {apy:.2f}%"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def main():
    apy = get_apy()
    if apy is None:
        print("APY non trovato")
        return
    print("APY =", apy)
    if apy < THRESHOLD:
        send_alert(apy)

if __name__ == "__main__":
    main()
