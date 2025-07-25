
import base64
import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import os
import csv
from datetime import datetime

def log_spam(msg_id, prob, snippet, logfile="spam_log.csv"):
    with open(logfile, mode="a", newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().isoformat(), msg_id, f"{prob:.5f}", snippet[:100]])
        if prob == 1.0:
            service.users().messages().trash(userId="me", id=msg_id).execute()
            print("🧹 Auto-moved to trash (100% confidence). Logged.")


SCOPES = ['https://mail.google.com/']  # full access

def gmail_authenticate():
    creds = None
    if os.path.exists('token.json'):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_messages(service, query, max_results=5000):
    print(f"🔍 Searching Gmail: {query}")
    result = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
    return result.get('messages', [])

def get_message_text(service, msg_id):
    try:
        msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        payload = msg.get('payload', {})
        parts = payload.get('parts', [])
        data = ''
        if parts:
            for part in parts:
                body = part.get('body', {}).get('data')
                if body:
                    data += base64.urlsafe_b64decode(body).decode('utf-8', errors='ignore')
        else:
            body = payload.get('body', {}).get('data')
            if body:
                data = base64.urlsafe_b64decode(body).decode('utf-8', errors='ignore')
        return data.strip()
    except Exception as e:
        print(f"⚠️ Error reading message: {e}")
        return ''

def load_spam_model():
    print("🧠 Training spam model...")
    df = pd.read_csv("https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv", sep="\t", names=["label", "text"])
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(df["text"])
    y = df["label"] == "spam"
    model = MultinomialNB()
    model.fit(X, y)
    return model, vectorizer

def scan_for_spam(service, model, vectorizer, query="older_than:1d", max_results=500):
    messages = get_messages(service, query, max_results)
    print(f"📥 {len(messages)} messages fetched.")

    for msg in messages:  # ✅ THIS is the required loop
        msg_id = msg["id"]
        text = get_message_text(service, msg_id)

        if not text or not text.strip():
            print(f"⚠️ Skipping empty message: {msg_id}")
            continue  # ✅ continue is valid here because it's inside a loop

        X = vectorizer.transform([text])
        prob = model.predict_proba(X)[0][1]
        is_spam = model.predict(X)[0]

        print(f"[DEBUG] Message ID: {msg_id} | Prob: {prob:.5f}")

        if is_spam and prob == 1.0:
            service.users().messages().trash(userId="me", id=msg_id).execute()
            log_spam(msg_id, prob, text)
            print(f"🧹 Auto-deleted spam message {msg_id} (100% confidence).")
        else:
            print(f"✔️ Skipped message {msg_id} (confidence: {prob:.2%})")


if __name__ == "__main__":
    print("🔐 Authenticating...")
    service = gmail_authenticate()

    model, vectorizer = load_spam_model()

    print("🔎 Scanning for spam...")
    scan_for_spam(service, model, vectorizer, query="older_than:0d")

    print("🎉 Done!")

    messages = get_messages(service, query="older_than:0d")  # or any query you want


    def extract_text(service, msg_id):
        try:
            message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            payload = message.get("payload", {})
            parts = payload.get("parts", [])

            text = ""

            if "data" in payload.get("body", {}):
                # single-part message
                text = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
            else:
                # multi-part message
                for part in parts:
                    if part.get("mimeType") == "text/plain" and "data" in part.get("body", {}):
                        data = part["body"]["data"]
                        text += base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

            return text.strip()
        except Exception as e:
            print(f"❌ Failed to extract text for message {msg_id}: {e}")
            return ""


    for msg in messages:
        msg_id = msg["id"]
        text = extract_text(service, msg_id)
        if not text.strip():
            print(f"⚠️ Skipping empty message: {msg_id}")
            continue

        # Vectorize and predict
        features = vectorizer.transform([text])
        is_spam = model.predict(features)[0] == 1
        prob = model.predict_proba(features)[0][1]

        print(f"[DEBUG] Message ID: {msg_id} | Prob: {prob:.5f}")

        if is_spam:
            if prob >= 0.9999:
                service.users().messages().trash(userId="me", id=msg_id).execute()
                log_spam(msg_id, prob, text)
                print(f"🧹 Auto-deleted spam message {msg_id} (100% confidence).")
            else:
                print("🚨 Spam detected, but not 100% confident — skipped.")
        else:
            print(f"✔️ Skipped message {msg_id} (confidence: {prob:.2%})")


