import os
import requests
from flask import Flask, render_template, request
import joblib
import re

app = Flask(__name__)

# ID الخاص بملف Google Drive
VECTOR_FILE_ID = "1vYmOBtA0U6xMr-h0VG4jWhENgolex8wL"
VECTOR_FILE_PATH = "tfidf_vectorizer_lr.pkl"

# دالة لتحميل الملف من Google Drive
def download_vectorizer():
    if not os.path.exists(VECTOR_FILE_PATH):
        print("📥 جاري تحميل tfidf_vectorizer_lr.pkl من Google Drive...")
        url = f"https://drive.google.com/uc?export=download&id={VECTOR_FILE_ID}"
        response = requests.get(url)
        with open(VECTOR_FILE_PATH, "wb") as f:
            f.write(response.content)
        print("✅ تم التحميل بنجاح.")

# تحميل الملف إذا لم يكن موجودًا
download_vectorizer()

# تحميل الموديل والـ TF-IDF
model = joblib.load("logistic_regression_phishing_model.pkl")
vectorizer = joblib.load(VECTOR_FILE_PATH)

# دالة تنظيف الرابط
def clean_url(url):
    url = url.lower()
    url = re.sub(r'https?:\/\/', '', url)
    url = re.sub(r'www\d*\.', '', url)
    url = re.sub(r':\d+', '', url)
    url = re.sub(r'[\?#].*', '', url)
    url = re.sub(r'[^a-z0-9\-\.\/]', ' ', url)
    url = re.sub(r'\s+', ' ', url)
    return url.strip()

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    probability = None

    if request.method == "POST":
        raw_url = request.form["url"]
        if not raw_url.strip():
            result = "❌ من فضلك أدخل رابطًا أولاً"
        else:
            cleaned = clean_url(raw_url)
            X = vectorizer.transform([cleaned])
            prediction = model.predict(X)[0]
            probability = round(model.predict_proba(X)[0][1] * 100, 2)
            result = "✅ الرابط آمن" if prediction == 1 else "⚠️ الرابط مشبوه"

    return render_template("index.html", result=result, probability=probability)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
