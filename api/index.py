from flask import Flask, render_template_string, request, jsonify
import qrcode
from PIL import Image
import io
import base64

# Create Flask app
app = Flask(__name__)

def create_vcard(first_name, last_name, phone, email, organization="", title="", website="", address=""):
    """Create a vCard string with contact information"""
    vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{first_name} {last_name}
N:{last_name};{first_name};;;
ORG:{organization}
TITLE:{title}
TEL:{phone}
EMAIL:{email}
URL:{website}
ADR:;;{address};;;;
END:VCARD"""
    return vcard

# Simple HTML template
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📱 vCard QR Generator</title>
    <meta name="description" content="Generate QR codes for instant contact sharing">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            margin: 0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            text-align: center;
            padding: 30px 20px;
        }
        .header h1 { font-size: 2rem; margin-bottom: 10px; }
        .form-container { padding: 40px; }
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .form-group { display: flex; flex-direction: column; }
        .form-group label {
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
        }
        .form-group input {
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
        }
        .form-group input:focus {
            outline: none;
            border-color: #4CAF50;
        }
        .generate-btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            cursor: pointer;
        }
        .result-container {
            margin-top: 30px;
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
            display: none;
        }
        .qr-code { max-width: 250px; width: 100%; }
        .error-message {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📱 vCard QR Generator</h1>
            <p>Create instant contact sharing QR codes</p>
        </div>
        
        <div class="form-container">
            <form id="vcardForm">
                <div class="form-grid">
                    <div class="form-group">
                        <label for="first_name">First Name *</label>
                        <input type="text" id="first_name" name="first_name" required>
                    </div>
                    <div class="form-group">
                        <label for="last_name">Last Name *</label>
                        <input type="text" id="last_name" name="last_name" required>
                    </div>
                    <div class="form-group">
                        <label for="phone">Phone Number *</label>
                        <input type="tel" id="phone" name="phone" required>
                    </div>
                    <div class="form-group">
                        <label for="email">Email Address *</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label for="organization">Organization</label>
                        <input type="text" id="organization" name="organization">
                    </div>
                    <div class="form-group">
                        <label for="title">Job Title</label>
                        <input type="text" id="title" name="title">
                    </div>
                    <div class="form-group">
                        <label for="website">Website</label>
                        <input type="url" id="website" name="website">
                    </div>
                    <div class="form-group">
                        <label for="address">Address</label>
                        <input type="text" id="address" name="address">
                    </div>
                </div>
                
                <button type="submit" class="generate-btn">🎯 Generate QR Code</button>
            </form>
            
            <div class="error-message" id="errorMessage"></div>
            
            <div class="result-container" id="resultContainer">
                <h3>✅ QR Code Generated!</h3>
                <img id="qrCode" class="qr-code" alt="Generated QR Code">
                <p>Scan with any QR code reader to add contact to your phone</p>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('vcardForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('qrCode').src = 'data:image/png;base64,' + result.qr_image;
                    document.getElementById('resultContainer').style.display = 'block';
                    document.getElementById('errorMessage').style.display = 'none';
                } else {
                    document.getElementById('errorMessage').textContent = result.error;
                    document.getElementById('errorMessage').style.display = 'block';
                    document.getElementById('resultContainer').style.display = 'none';
                }
            } catch (error) {
                document.getElementById('errorMessage').textContent = 'Error: ' + error.message;
                document.getElementById('errorMessage').style.display = 'block';
                document.getElementById('resultContainer').style.display = 'none';
            }
        });
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/generate', methods=['POST'])
def generate_qr():
    try:
        # Get form data
        data = request.get_json() if request.is_json else request.form
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'phone', 'email']
        for field in required_fields:
            if not data.get(field, '').strip():
                return jsonify({
                    'success': False, 
                    'error': f"Please fill in {field.replace('_', ' ').title()}"
                })
        
        # Create vCard
        vcard = create_vcard(
            data.get('first_name', '').strip(),
            data.get('last_name', '').strip(),
            data.get('phone', '').strip(),
            data.get('email', '').strip(),
            data.get('organization', '').strip(),
            data.get('title', '').strip(),
            data.get('website', '').strip(),
            data.get('address', '').strip()
        )
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(vcard)
        qr.make(fit=True)
        
        # Create image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for display
        img_buffer = io.BytesIO()
        qr_img.save(img_buffer, format='PNG')
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'qr_image': img_base64,
            'message': 'QR Code generated successfully!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Error generating QR code: {str(e)}"
        })

# CRITICAL: Vercel needs this exact export format
def handler(request):
    return app

# Alternative export format that Vercel also accepts
if __name__ != '__main__':
    # This makes the app available as a module-level variable
    application = app