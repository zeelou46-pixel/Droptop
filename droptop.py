import os
import uuid
import hashlib
import secrets
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template_string, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)

generated_pages = {}

def get_news_text():
    news_file = 'news.txt'
    if os.path.exists(news_file):
        with open(news_file, 'r', encoding='utf-8') as f:
            news = f.read().strip()
            if news:
                return news
    default = "🎉 DROP THAT SH*T - Generate unique location pages! | 🔒 Password protect your links | 📍 Live GPS tracking | 💀 Share with anyone! | ✨ Each click = brand new unique page"
    with open(news_file, 'w', encoding='utf-8') as f:
        f.write(default)
    return default

LOCATION_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📍 Live Location Tracker</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .news-ticker {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background: #000000cc;
            backdrop-filter: blur(5px);
            z-index: 1000;
            border-bottom: 1px solid #ff3366;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        .ticker-wrap {
            width: 100%;
            overflow: hidden;
            background: #0a0a0a;
            padding: 8px 0;
        }
        .ticker {
            display: inline-block;
            white-space: nowrap;
            animation: scrollTicker 25s linear infinite;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            font-size: 14px;
            color: #00ffcc;
            text-shadow: 0 0 5px #00ffcc;
            letter-spacing: 1px;
        }
        @keyframes scrollTicker {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
            animation: fadeIn 0.5s ease;
            margin-top: 60px;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .header { text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #f0f0f0; }
        .live-badge { background: #ff3366; color: white; display: inline-block; padding: 5px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.6; } 100% { opacity: 1; } }
        h1 { color: #333; margin-top: 15px; font-size: 24px; }
        .custom-message {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 12px 15px;
            margin: 15px 0;
            border-radius: 8px;
            color: #856404;
            font-family: monospace;
            font-size: 14px;
            word-break: break-word;
            white-space: pre-wrap;
        }
        .location-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; padding: 20px; margin: 20px 0; color: white; text-align: center; }
        .coordinates { font-size: 18px; font-family: monospace; margin: 10px 0; word-break: break-all; }
        .map-link { display: inline-block; background: white; color: #667eea; padding: 10px 20px; border-radius: 25px; text-decoration: none; margin-top: 10px; font-weight: bold; transition: transform 0.2s; }
        .map-link:hover { transform: translateY(-2px); }
        .info { background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 15px 0; font-size: 14px; color: #666; }
        button { background: #ff3366; color: white; border: none; padding: 12px 24px; border-radius: 25px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 10px; font-weight: bold; transition: transform 0.2s; }
        button:hover { transform: scale(1.02); }
        .refresh-btn { background: #28a745; }
        .loading { text-align: center; padding: 20px; }
        .spinner { border: 3px solid #f3f3f3; border-top: 3px solid #667eea; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .error { background: #fee; color: #c33; padding: 10px; border-radius: 8px; text-align: center; margin: 10px 0; }
        .page-id { font-family: monospace; color: #999; font-size: 12px; text-align: center; margin-top: 20px; }
        .copyright {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            font-size: 12px;
            color: #999;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="news-ticker">
        <div class="ticker-wrap">
            <div class="ticker">{{ news_text }} &nbsp; ✨ &nbsp; {{ news_text }} &nbsp; ✨ &nbsp; {{ news_text }}</div>
        </div>
    </div>
    <div class="container">
        <div class="header">
            <div class="live-badge">🔴 LIVE LOCATION</div>
            <h1>📍 {{page_title}}</h1>
            <div class="page-id">Page ID: {{page_id}}</div>
        </div>
        {% if custom_message %}
        <div class="custom-message">
            💬 <strong>Message from creator:</strong><br>
            {{ custom_message }}
        </div>
        {% endif %}
        <div id="locationContent">
            <div class="loading">
                <div class="spinner"></div>
                <p style="margin-top: 10px;">Getting your location...</p>
            </div>
        </div>
        <div class="info">
            💡 <strong>How this works:</strong><br>
            • This page shows your current GPS location<br>
            • Click refresh to update your position<br>
            • Share this link with others to see their location
        </div>
        <div class="copyright">© 2006 made by Z</div>
    </div>
    <script>
        function getLocation() {
            const locationDiv = document.getElementById('locationContent');
            if (!navigator.geolocation) {
                locationDiv.innerHTML = '<div class="error">❌ Geolocation is not supported by your browser</div>';
                return;
            }
            locationDiv.innerHTML = `<div class="loading"><div class="spinner"></div><p>Fetching your precise location...</p></div>`;
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    const accuracy = position.coords.accuracy;
                    const mapsUrl = `https://www.google.com/maps?q=${lat},${lng}`;
                    const timestamp = new Date().toLocaleString();
                    locationDiv.innerHTML = `
                        <div class="location-box">
                            <div style="font-size: 14px; margin-bottom: 10px;">📍 YOUR CURRENT LOCATION</div>
                            <div class="coordinates">
                                <strong>Latitude:</strong> ${lat.toFixed(6)}<br>
                                <strong>Longitude:</strong> ${lng.toFixed(6)}
                            </div>
                            <div style="font-size: 12px; margin-top: 5px;">Accuracy: ±${Math.round(accuracy)} meters</div>
                            <a href="${mapsUrl}" target="_blank" class="map-link">🗺️ Open in Google Maps</a>
                        </div>
                        <div class="info"><strong>🕒 Captured at:</strong> ${timestamp}<br><strong>📍 Coordinates:</strong> ${lat}, ${lng}</div>
                        <button onclick="copyLocation(${lat}, ${lng})">📋 Copy Coordinates</button>
                        <button onclick="getLocation()" class="refresh-btn">🔄 Refresh Location</button>
                    `;
                },
                (error) => {
                    let errorMessage = '';
                    switch(error.code) {
                        case error.PERMISSION_DENIED: errorMessage = 'Location access denied. Please enable location services.'; break;
                        case error.POSITION_UNAVAILABLE: errorMessage = 'Location information unavailable.'; break;
                        case error.TIMEOUT: errorMessage = 'Location request timed out.'; break;
                        default: errorMessage = 'An unknown error occurred.';
                    }
                    locationDiv.innerHTML = `<div class="error">❌ ${errorMessage}<br><br><button onclick="getLocation()" style="background: #ff3366; width: auto; padding: 8px 16px;">🔄 Try Again</button></div>`;
                },
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
            );
        }
        function copyLocation(lat, lng) {
            const text = `${lat}, ${lng}`;
            navigator.clipboard.writeText(text).then(() => alert('✅ Coordinates copied to clipboard!')).catch(() => alert('❌ Failed to copy'));
        }
        getLocation();
    </script>
</body>
</html>
'''

MAIN_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 DROP THAT SH*T - Generate Location Page</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Impact', 'Arial Black', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow-x: hidden;
            position: relative;
            padding-top: 70px;
        }
        .news-ticker {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background: #000000cc;
            backdrop-filter: blur(5px);
            z-index: 1000;
            border-bottom: 1px solid #ff3366;
            box-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }
        .ticker-wrap {
            width: 100%;
            overflow: hidden;
            background: #0a0a0a;
            padding: 10px 0;
        }
        .ticker {
            display: inline-block;
            white-space: nowrap;
            animation: scrollTicker 25s linear infinite;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            font-size: 15px;
            color: #ff3366;
            text-shadow: 0 0 5px #ff3366;
            letter-spacing: 1px;
        }
        @keyframes scrollTicker {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }
        .particle-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
        }
        .particle {
            position: absolute;
            background: rgba(255,51,102,0.3);
            border-radius: 50%;
            animation: float 10s infinite;
        }
        @keyframes float {
            0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
        }
        .container {
            text-align: center;
            z-index: 10;
            padding: 20px;
            width: 100%;
            max-width: 600px;
            animation: slideUp 0.5s ease;
        }
        @keyframes slideUp {
            from { transform: translateY(50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        h1 {
            color: #ff3366;
            font-size: 64px;
            text-shadow: 0 0 20px rgba(255,51,102,0.5);
            margin-bottom: 20px;
            letter-spacing: 5px;
            animation: shake 2s ease-in-out infinite;
        }
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
        .subtitle {
            color: #fff;
            font-size: 18px;
            margin-bottom: 40px;
            font-family: 'Courier New', monospace;
        }
        .message-input {
            background: rgba(0,0,0,0.7);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            border: 1px solid #ff3366;
        }
        .message-input label {
            color: white;
            font-family: 'Courier New', monospace;
            display: block;
            margin-bottom: 10px;
        }
        .message-input textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ff3366;
            border-radius: 10px;
            background: rgba(255,255,255,0.1);
            color: white;
            font-size: 14px;
            font-family: monospace;
            resize: vertical;
            min-height: 80px;
        }
        .message-input textarea:focus {
            outline: none;
            background: rgba(255,255,255,0.2);
        }
        .password-option {
            background: rgba(0,0,0,0.7);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            border: 1px solid #ff3366;
        }
        .checkbox-label {
            color: white;
            font-family: 'Courier New', monospace;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin-bottom: 15px;
        }
        .checkbox-label input {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }
        .password-input {
            display: none;
            margin-top: 15px;
        }
        .password-input input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ff3366;
            border-radius: 10px;
            background: rgba(255,255,255,0.1);
            color: white;
            font-size: 16px;
            font-family: monospace;
        }
        .password-input input:focus {
            outline: none;
            background: rgba(255,255,255,0.2);
        }
        .generate-btn {
            background: linear-gradient(135deg, #ff3366, #ff6699);
            border: none;
            color: white;
            font-size: 32px;
            font-weight: bold;
            padding: 25px 50px;
            border-radius: 60px;
            cursor: pointer;
            margin: 20px 0;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(255,51,102,0.4);
            font-family: 'Impact', 'Arial Black', sans-serif;
            text-transform: uppercase;
            letter-spacing: 3px;
            width: 100%;
        }
        .generate-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 15px 40px rgba(255,51,102,0.6);
        }
        .generate-btn:active {
            transform: scale(0.95);
        }
        .generated-link {
            background: rgba(0,0,0,0.8);
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
            animation: fadeIn 0.5s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .generated-link a {
            color: #ff6699;
            text-decoration: none;
            word-break: break-all;
            font-family: monospace;
            font-size: 14px;
        }
        .generated-link a:hover {
            text-decoration: underline;
        }
        .copy-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
            font-size: 14px;
        }
        .copy-btn:hover {
            background: #34ce57;
        }
        .info {
            color: rgba(255,255,255,0.6);
            font-size: 12px;
            margin-top: 30px;
            font-family: monospace;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid #fff;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 0.6s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .copyright {
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid rgba(255,255,255,0.2);
            font-size: 11px;
            color: rgba(255,255,255,0.4);
            font-family: monospace;
        }
        @media (max-width: 600px) {
            h1 { font-size: 36px; }
            .generate-btn { font-size: 24px; padding: 20px 30px; }
            body { padding-top: 60px; }
        }
    </style>
</head>
<body>
    <div class="news-ticker">
        <div class="ticker-wrap">
            <div class="ticker">{{ news_text }} &nbsp; ✨ &nbsp; {{ news_text }} &nbsp; ✨ &nbsp; {{ news_text }}</div>
        </div>
    </div>
    <div class="particle-bg" id="particles"></div>
    <div class="container">
        <h1>💀 DROP THAT SH*T 💀</h1>
        <div class="subtitle">Generate a unique location tracking page</div>
        
        <div class="message-input">
            <label>💬 Optional: Add a message to show on the page</label>
            <textarea id="customMessage" placeholder="Enter any message here... (e.g., 'Meet me here!', 'This is my secret spot', etc.)" maxlength="500"></textarea>
            <div style="font-size: 11px; color: #888; text-align: right; margin-top: 5px;">Max 500 characters</div>
        </div>
        
        <div class="password-option">
            <label class="checkbox-label">
                <input type="checkbox" id="protectCheckbox">
                🔒 Protect with password
            </label>
            <div class="password-input" id="passwordDiv">
                <input type="password" id="pagePassword" placeholder="Enter password for this page">
            </div>
        </div>
        
        <button class="generate-btn" onclick="generatePage()">
            🚀 GENERATE UNIQUE PAGE 🚀
        </button>
        
        <div class="generated-link" id="generatedLink">
            <strong style="color: #28a745;">✅ PAGE GENERATED!</strong><br>
            <a href="#" id="pageLink" target="_blank"></a><br>
            <button class="copy-btn" onclick="copyLink()">📋 Copy Link</button>
        </div>
        
        <div class="info">
            💡 Each click creates a BRAND NEW unique page<br>
            📍 Visitors will see their GPS location<br>
            🔗 Share the link with anyone
        </div>
        
        <div class="copyright">© 2006 made by Z</div>
    </div>
    
    <script>
        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            const size = Math.random() * 5 + 2;
            particle.style.width = size + 'px';
            particle.style.height = size + 'px';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 10 + 's';
            particle.style.animationDuration = Math.random() * 10 + 5 + 's';
            document.getElementById('particles').appendChild(particle);
        }
        
        document.getElementById('protectCheckbox').onchange = function() {
            document.getElementById('passwordDiv').style.display = this.checked ? 'block' : 'none';
        };
        
        async function generatePage() {
            const button = document.querySelector('.generate-btn');
            const originalText = button.innerHTML;
            button.innerHTML = '⏳ GENERATING...';
            button.disabled = true;
            
            const protect = document.getElementById('protectCheckbox').checked;
            const password = protect ? document.getElementById('pagePassword').value : null;
            const customMessage = document.getElementById('customMessage').value.trim();
            
            if (protect && (!password || password.trim() === '')) {
                alert('Please enter a password for protection');
                button.innerHTML = originalText;
                button.disabled = false;
                return;
            }
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        protect: protect,
                        password: password,
                        custom_message: customMessage || null
                    })
                });
                if (!response.ok) throw new Error('Server error: ' + response.status);
                const data = await response.json();
                if (data.success) {
                    const linkDiv = document.getElementById('generatedLink');
                    const pageLink = document.getElementById('pageLink');
                    const fullUrl = window.location.origin + data.url;
                    pageLink.href = data.url;
                    pageLink.textContent = fullUrl;
                    linkDiv.style.display = 'block';
                    button.style.background = '#28a745';
                    setTimeout(() => button.style.background = 'linear-gradient(135deg, #ff3366, #ff6699)', 1000);
                } else {
                    alert('Error: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                alert('Failed to generate page: ' + error.message);
            } finally {
                button.innerHTML = originalText;
                button.disabled = false;
            }
        }
        
        function copyLink() {
            const link = document.getElementById('pageLink').href;
            if (link) navigator.clipboard.writeText(link).then(() => alert('✅ Link copied to clipboard!')).catch(() => alert('❌ Failed to copy link'));
        }
    </script>
</body>
</html>
'''

PASSWORD_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔒 Password Protected</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: monospace;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: rgba(0,0,0,0.9);
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            max-width: 400px;
            animation: fadeIn 0.5s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.9); }
            to { opacity: 1; transform: scale(1); }
        }
        h2 { color: #ff3366; margin-bottom: 20px; }
        input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 2px solid #ff3366;
            border-radius: 10px;
            background: rgba(255,255,255,0.1);
            color: white;
            font-size: 16px;
        }
        button {
            background: #ff3366;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
            width: 100%;
        }
        button:hover { background: #ff6699; }
        .error {
            color: #ff6666;
            margin-top: 10px;
            display: none;
        }
        .copyright {
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid rgba(255,255,255,0.2);
            font-size: 10px;
            color: rgba(255,255,255,0.3);
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔒 Password Required</h2>
        <p style="color: white; margin-bottom: 20px;">This location page is password protected</p>
        <input type="password" id="password" placeholder="Enter password" autofocus>
        <button onclick="verifyPassword()">Access Location</button>
        <div class="error" id="errorMsg">❌ Wrong password!</div>
        <div class="copyright">© 2006 made by Z</div>
    </div>
    <script>
        async function verifyPassword() {
            const password = document.getElementById('password').value;
            const pageId = window.location.pathname.split('/')[2];
            try {
                const response = await fetch(`/verify/${pageId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password: password })
                });
                if (response.ok) {
                    const data = await response.json();
                    window.location.href = data.redirect;
                } else {
                    document.getElementById('errorMsg').style.display = 'block';
                    setTimeout(() => document.getElementById('errorMsg').style.display = 'none', 2000);
                }
            } catch (error) {
                alert('Verification failed: ' + error.message);
            }
        }
        document.getElementById('password').addEventListener('keypress', (e) => { if (e.key === 'Enter') verifyPassword(); });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(MAIN_PAGE, news_text=get_news_text())

@app.route('/generate', methods=['POST'])
def generate_page():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Invalid request'}), 400
        
        protect = data.get('protect', False)
        password = data.get('password')
        custom_message = data.get('custom_message', '')
        
        page_id = str(uuid.uuid4())[:8]
        page_data = {
            'id': page_id,
            'protected': protect,
            'created_at': datetime.now().isoformat(),
            'views': 0,
            'custom_message': custom_message
        }
        if protect and password:
            page_data['password_hash'] = hashlib.sha256(password.encode()).hexdigest()
        
        generated_pages[page_id] = page_data
        url = f'/protected/{page_id}' if protect else f'/location/{page_id}'
        return jsonify({'success': True, 'url': url, 'page_id': page_id})
    except Exception:
        return jsonify({'success': False, 'error': 'Server error'}), 500

@app.route('/location/<page_id>')
def show_location(page_id):
    if page_id not in generated_pages:
        return "Page not found or expired", 404
    page_data = generated_pages[page_id]
    if page_data.get('protected') and not request.args.get('verified'):
        return redirect(url_for('password_protect', page_id=page_id))
    page_data['views'] = page_data.get('views', 0) + 1
    generated_pages[page_id] = page_data
    return render_template_string(
        LOCATION_PAGE,
        page_id=page_id,
        page_title="Location Tracker",
        news_text=get_news_text(),
        custom_message=page_data.get('custom_message', '')
    )

@app.route('/protected/<page_id>')
def password_protect(page_id):
    if page_id not in generated_pages:
        return "Page not found", 404
    if not generated_pages[page_id].get('protected'):
        return redirect(url_for('show_location', page_id=page_id))
    return render_template_string(PASSWORD_PAGE)

@app.route('/verify/<page_id>', methods=['POST'])
def verify_password(page_id):
    if page_id not in generated_pages:
        return jsonify({'error': 'Page not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
    input_password = data.get('password', '')
    input_hash = hashlib.sha256(input_password.encode()).hexdigest()
    stored_hash = generated_pages[page_id].get('password_hash')
    if stored_hash and input_hash == stored_hash:
        return jsonify({'success': True, 'redirect': f'/location/{page_id}?verified=true'})
    return jsonify({'error': 'Wrong password'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)