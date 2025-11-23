import os
import requests
import socket
import time

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD = 13.0

API_URL = "https://app.exponent.finance/api/v1/farms/overview"


# -----------------------------------------
# Funzione DNS Fallback su Cloudflare
# -----------------------------------------
def resolve_hostname(hostname):
    try:
        # DNS normale
        return socket.gethostbyname(hostname)
    except:
        # fallback su DNS Cloudflare
        dns = "1.1.1.1"
        try:
            return socket.gethostbyname_ex(hostname, None, [dns])[2][0]
        except:
            return None


# -----------------------------------------
# Chiamata API con retry e fallback DNS
# -----------------------------------------
def robust_get(url, retries=5, timeout=10):
    parsed = requests.utils.urlparse(url)
    host = parsed.hostname

    ip = resolve_hostname(host)
    if ip is None:
        print("❌ DNS impossibile da risolvere:", host)
        return None

    # Ricrea URL usando IP al posto dell'hostname
    new_url = url.replace(host, ip)

    headers = {"Host": host}

    for attempt in range(1, retries + 1):
        try:
            print(f"Tentativo {attempt}/{retries} → {new_url}")
            r = requests.get(new_url, headers=headers, timeout=timeout)
            return r
        except Exception as e:
            print("Errore tentativo", attempt, ":", e)
            time.sleep(1)

    return None


# -----------------------------------------
# Estrazione APY
# -----------------------------------------
def get_apy():
    r = robust_get(API_URL)

    if r is None:
        print("❌ Impossibile contattare l'API.")
        return None

    try:
        data = r.json()
    except:
        print("❌ Errore nel parsing JSON")
        return None

    try:
        for farm in data["data"]:
            if "YT-eUSX" in farm["symbol"]:
                return farm["ytImpliedRateAnnualizedPct"] * 100
    except Exception as e:
        print("Errore parsing struttura:", e)

    return None


# -----------------------------------------
# Funzione invio Telegram
# -----------------------------------------
def send_alert(apy):
    msg = f"⚠️ APY sotto soglia!\nValore attuale: {apy:.2f}%"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


# -----------------------------------------
# MAIN
# -----------------------------------------
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
