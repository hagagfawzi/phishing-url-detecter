from flask import Flask, render_template, request
import joblib
import re

app = Flask(__name__)

# تحميل الموديل والـ TF-IDF
model = joblib.load("logistic_regression_phishing_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer_lr.pkl")

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
    app.run(debug=True)

