import requests

TOKEN = "8201825302:AAH4BPyKSxuTfg1AFAz-rFlAv0mvM-vzxag"
url = f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo"
resp = requests.get(url).json()
print(resp)
