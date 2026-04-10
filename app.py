from flask import Flask, render_template, request, redirect, url_for, make_response, flash, jsonify
import time, base64
# تأكد أن ملف crypto_helpers.py موجود في نفس المجلد
from crypto_helpers import (generate_mac, verify_mac, generate_rsa_keys, 
                            sign_data, verify_signature)

app = Flask(__name__)
app.secret_key = "secure_assignment_key"

# مخزن البيانات المؤقت
vault = {
    "private_key": None,
    "public_key": None,
    "last_signature": None,
    "last_content": None
}

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    # إنشاء بيانات الكوكي الأصلية (user)
    payload = f"{username}|user|{int(time.time()) + 8}"
    mac = generate_mac(payload)
    
    # التوجيه لصفحة الداشبورد مع وضع الكوكيز
    resp = make_response(redirect(url_for('dashboard')))
    resp.set_cookie('user_payload', payload)
    resp.set_cookie('user_mac', mac)
    return resp

@app.route('/dashboard')
def dashboard():
    payload = request.cookies.get('user_payload')
    mac = request.cookies.get('user_mac')

    if not payload or not mac:
        return redirect(url_for('index'))

    # 1. فحص التلاعب (الـ MAC)
    if not verify_mac(payload, mac):
        try:
            username = payload.split('|')[0]
        except:
            username = "User"
            
        corrected_payload = f"{username}|user|{int(time.time()) +20}"
        corrected_mac = generate_mac(corrected_payload)

        resp = make_response(render_template('dashboard.html', 
                             username=username, 
                             role="user", 
                             payload=corrected_payload, 
                             mac=corrected_mac,
                             error="TAMPERING DETECTED! ❌ Your role was reset to 'user' for security."))
        
        resp.set_cookie('user_payload', corrected_payload)
        resp.set_cookie('user_mac', corrected_mac)
        return resp

    # 2. فحص انتهاء الوقت (Expiration Logic) - الجزء اللي كان ناقص
    try:
        u, r, e = payload.split('|')
        
        # تحويل وقت الانتهاء من نص إلى رقم وقارنيه بالوقت الحالي
        # 2. فحص انتهاء الوقت (Expiration Logic)
        # 2. فحص انتهاء الوقت
        if int(time.time()) > int(e):
            # نرسل الـ error كمتغير مباشر لصفحة اللوجين وليس كـ flash
            resp = make_response(render_template('login.html', error="Session Expired! ⏳ Please login again."))
            resp.set_cookie('user_payload', '', expires=0)
            resp.set_cookie('user_mac', '', expires=0)
            return resp

        # لو الكوكي سليمة والوقت لسه مخلصش، ادخل عادي
        return render_template('dashboard.html', username=u, role=r, payload=payload, mac=mac)
    
    except Exception as ex:
        print(f"Error parsing cookie: {ex}")
        return "Invalid Data format", 400

@app.route('/signatures', methods=['GET', 'POST'])
def signatures():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == "generate":
            vault["private_key"], vault["public_key"] = generate_rsa_keys()
            flash("RSA Keys Generated Successfully!")
        elif action == "sign":
            content = request.form.get('content')
            if vault["private_key"]:
                vault["last_signature"] = sign_data(vault["private_key"], content)
                vault["last_content"] = content
                flash("Signed Successfully!")
    
    sig_hex = base64.b64encode(vault["last_signature"]).decode() if vault["last_signature"] else None
    return render_template('signatures.html', sig=sig_hex, content=vault["last_content"])

@app.route('/verify', methods=['POST'])
def verify():
    content = request.form.get('content')
    is_valid = verify_signature(vault["public_key"], content, vault["last_signature"])
    return render_template('signatures.html', 
                           verification_result="Valid ✅" if is_valid else "Invalid ❌",
                           sig=base64.b64encode(vault["last_signature"]).decode() if vault["last_signature"] else None,
                           content=content)

@app.route('/bonus')
def bonus():
    return render_template('attacks.html')

# مسارات هجمات البونص
@app.route('/bonus/key-substitution', methods=['POST'])
def key_substitution():
    attacker_priv, attacker_pub = generate_rsa_keys()
    malicious_msg = "Transfer $10,000 to Attacker"
    malicious_sig = sign_data(attacker_priv, malicious_msg)
    vault["public_key"] = attacker_pub 
    return jsonify({"status": "Success", "msg": malicious_msg})

@app.route('/bonus/message-key-substitution', methods=['POST'])
def message_key_substitution():
    attacker_priv, attacker_pub = generate_rsa_keys()
    fake_msg = "Fake Command"
    is_valid = verify_signature(attacker_pub, fake_msg, sign_data(attacker_priv, fake_msg))
    return jsonify({"attack": "Message Key Substitution", "verified": is_valid})

if __name__ == '__main__':
    app.run(debug=True)