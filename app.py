from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import re
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

# ---------------------------
# Helpers: phishing scoring
# ---------------------------

SUSPICIOUS_ACTION_WORDS = [
    "verify", "confirm", "click", "reset", "submit", "sign in", "login", "log in",
    "update", "press", "open", "respond", "act now", "immediately"
]

CONSEQUENCE_WORDS = [
    "locked", "suspended", "disabled", "removed", "terminated", "deactivated",
    "access removed", "account will be", "lose access"
]

CREDENTIAL_WORDS = [
    "password", "otp", "one-time", "one time", "code", "login", "credentials", "pin"
]

BRAND_WORDS = [
    "penn state", "psu", "microsoft", "google", "apple", "service desk", "it desk",
    "gmail", "amazon", "bank", "paypal"
]

AUTOMATED_TEMPLATE_PHRASES = [
    "do not reply", "this is an automated", "automated email", "please do not reply"
]


def extract_urls(text: str):
    url_regex = r"(https?://[^\s)]+)"
    return re.findall(url_regex, text, flags=re.IGNORECASE)


def domain_looks_like_brand(domain: str, brand_keywords=None):
    if brand_keywords is None:
        brand_keywords = ["psu", "pennstate", "penn-state", "microsoft", "google", "apple"]

    d = (domain or "").lower()

    if any(k in d for k in brand_keywords):
        trusted_suffixes = (
            "psu.edu",
            "pennstate.edu",
            "microsoft.com",
            "google.com",
            "apple.com"
        )
        if not d.endswith(trusted_suffixes):
            return True
    return False


def analyze_message(message: str):
    msg = (message or "").strip()
    lower = msg.lower()

    score = 0
    breakdown = []
    flags = []

    # Links
    urls = extract_urls(msg)
    if urls:
        score += 25
        breakdown.append(("Link(s) present", 25))
        flags.append(f"Contains link(s): {', '.join(urls[:3])}{'...' if len(urls) > 3 else ''}")

        try:
            parsed = urlparse(urls[0])
            domain = parsed.netloc
            if domain_looks_like_brand(domain):
                score += 15
                breakdown.append(("Look-alike domain pattern", 15))
                flags.append("Domain appears to imitate a trusted brand but may not be official.")
        except Exception:
            pass

    # Action request language
    if any(w in lower for w in SUSPICIOUS_ACTION_WORDS):
        score += 15
        breakdown.append(("Action request language", 15))
        flags.append("Requests urgent action (verify/confirm/click/reset/submit/etc.).")

    # Threats / consequences
    if any(w in lower for w in CONSEQUENCE_WORDS):
        score += 20
        breakdown.append(("Threats / consequences / access removed", 20))
        flags.append("Mentions consequences (removed/disabled/locked/suspended/etc.).")

    # Compliance / policy pressure
    if "compliance" in lower or "policy" in lower or "requirement" in lower:
        score += 10
        breakdown.append(("Compliance / policy pressure", 10))
        flags.append("Mentions compliance / policy pressure.")

    # Automated template signals
    if any(p in lower for p in AUTOMATED_TEMPLATE_PHRASES):
        score += 5
        breakdown.append(("Automated template signals", 5))
        flags.append("Says it's automated / do not reply (template-like signal).")

    # Brand/org mention
    if any(b in lower for b in BRAND_WORDS):
        score += 10
        breakdown.append(("Brand/org mention (possible impersonation)", 10))
        flags.append("May impersonate a known organization or service.")

    # Mentions credentials
    if any(c in lower for c in CREDENTIAL_WORDS):
        score += 15
        breakdown.append(("Mentions credentials (password/OTP/login)", 15))
        flags.append("Mentions credentials (password/OTP/login/code).")

    # Urgency language
    if "urgent" in lower or "immediately" in lower or "asap" in lower:
        score += 10
        breakdown.append(("Urgency language", 10))
        flags.append("Uses urgency language.")

    score = min(score, 100)

    if score >= 70:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "message": msg,
        "score": score,
        "level": level,
        "breakdown": breakdown,
        "flags": flags
    }


# ---------------------------
# Pages (HTML)
# ---------------------------

@app.get("/")
def index():
    return render_template("index.html", message="", result=None)


@app.post("/analyze")
def phishing_check():
    message = request.form.get("message", "")
    result = analyze_message(message)
    return render_template("index.html", message=message, result=result)


@app.get("/chat")
def chat_page():
    return render_template("chat.html")


# ---------------------------
# API (JSON / form)
# ---------------------------

@app.route("/api/analyze", methods=["POST", "OPTIONS"])
def api_analyze():
    message = ""

    if request.form:
        message = (request.form.get("message") or "").strip()
    else:
        data = request.get_json(silent=True) or {}
        message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "No message provided"}), 400

    return jsonify(analyze_message(message))


@app.post("/api/chat")
def api_chat():
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()

    if not msg:
        return jsonify({"reply": "Type a message first."}), 400

    result = analyze_message(msg)

    if result["level"] == "HIGH":
        reply = f"HIGH RISK ({result['score']}/100)"
    elif result["level"] == "MEDIUM":
        reply = f"MEDIUM RISK ({result['score']}/100)"
    else:
        reply = f"LOW RISK ({result['score']}/100)"

    flags_line = "Flags: " + " | ".join(result["flags"]) if result["flags"] else "Flags: None detected."

    return jsonify({
        "reply": reply,
        "flags": flags_line,
        "level": result["level"],
        "score": result["score"]
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)