import requests

TOKEN = "8383944385:AAEKFHCb4kTvX8ftR8YhWSmzEv8jXpBkmfY"
WEBHOOK_URL = "https://emmaconsultantbot-production-96cc.up.railway.app/webhook"

# 1️⃣ Check current webhook info
resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo").json()
print("Webhook info:", resp)

# 2️⃣ Delete old webhook (optional, ensures clean start)
delete_resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true").json()
print("Delete webhook:", delete_resp)

# 3️⃣ Set new webhook
set_resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}").json()
print("Set webhook:", set_resp)
