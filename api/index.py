from flask import Flask, render_template_string, request, jsonify
import qrcode
from PIL import Image
import io
import base64
import os

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

# Inline HTML template (since Vercel serverless functions need everything in one file)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📱 vCard QR Generator</title>
    <meta name="description" content="Generate QR codes for instant contact sharing">
    <link rel="apple-touch-icon" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            text-align: center;
            padding: 30px 20px;
        }
        
        .header h1 {
            font-size: 2rem;
            margin-bottom: 10px;
            font-weight: 600;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 1.1rem;
        }
        
        .form-container {
            padding: 40px;
        }
        
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
        }
        
        .form-group label {
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .form-group input {
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: #f9f9f9;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #4CAF50;
            background: white;
            box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
        }
        
        .form-group.required label::after {
            content: ' *';
            color: #e74c3c;
        }
        
        .generate-btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .generate-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
        }
        
        .generate-btn:active {
            transform: translateY(0);
        }
        
        .generate-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .result-container {
            margin-top: 30px;
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
            border: 2px dashed #ddd;
            display: none;
        }
        
        .result-container.show {
            display: block;
            animation: fadeInUp 0.5s ease;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .qr-code-container {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
            display: inline-block;
        }
        
        .qr-code {
            max-width: 250px;
            width: 100%;
            height: auto;
            border-radius: 10px;
        }
        
        .download-btn, .share-btn {
            display: inline-block;
            margin: 10px;
            padding: 12px 25px;
            background: #2196F3;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            font-size: 14px;
        }
        
        .share-btn {
            background: #FF9800;
        }
        
        .download-btn:hover, .share-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        .error-message {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #c62828;
            display: none;
        }
        
        .success-message {
            background: #e8f5e8;
            color: #2e7d32;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #4caf50;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #4CAF50;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9rem;
        }
        
        .preview-section {
            background: #f0f8ff;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid #e3f2fd;
        }
        
        .preview-section h3 {
            color: #1976d2;
            margin-bottom: 15px;
        }
        
        .contact-preview {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            text-align: left;
        }
        
        .contact-preview .contact-item {
            margin: 5px 0;
            display: flex;
            align-items: center;
        }
        
        .contact-preview .contact-item strong {
            min-width: 80px;
            color: #333;
        }
        
        /* iOS Responsive Design */
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            .container {
                border-radius: 15px;
            }
            
            .header {
                padding: 20px 15px;
            }
            
            .header h1 {
                font-size: 1.6rem;
            }
            
            .form-container {
                padding: 20px;
            }
            
            .form-grid {
                grid-template-columns: 1fr;
                gap: 15px;
            }
            
            .qr-code {
                max-width: 200px;
            }
            
            .qr-code-container {
                padding: 20px;
            }
        }
        
        /* iOS Safari specific styles */
        @supports (-webkit-touch-callout: none) {
            .form-group input {
                -webkit-appearance: none;
                border-radius: 10px;
            }
            
            .generate-btn {
                -webkit-appearance: none;
                border-radius: 12px;
            }
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            body {
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            }
            
            .container {
                background: rgba(52, 73, 94, 0.95);
                color: #ecf0f1;
            }
            
            .form-group input {
                background: #34495e;
                border-color: #4a6741;
                color: #ecf0f1;
            }
            
            .form-group input:focus {
                background: #2c3e50;
                border-color: #4CAF50;
            }
            
            .result-container {
                background: #34495e;
                border-color: #4a6741;
            }
            
            .preview-section {
                background: #2c3e50;
                border-color: #4a6741;
            }
            
            .contact-preview {
                background: #34495e;
                color: #ecf0f1;
            }
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
                    <div class="form-group required">
                        <label for="first_name">First Name</label>
                        <input type="text" id="first_name" name="first_name" required>
                    </div>
                    
                    <div class="form-group required">
                        <label for="last_name">Last Name</label>
                        <input type="text" id="last_name" name="last_name" required>
                    </div>
                    
                    <div class="form-group required">
                        <label for="phone">Phone Number</label>
                        <input type="tel" id="phone" name="phone" required>
                    </div>
                    
                    <div class="form-group required">
                        <label for="email">Email Address</label>
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
                        <input type="url" id="website" name="website" placeholder="https://example.com">
                    </div>
                    
                    <div class="form-group">
                        <label for="address">Address</label>
                        <input type="text" id="address" name="address">
                    </div>
                </div>
                
                <div class="preview-section" id="previewSection" style="display: none;">
                    <h3>Contact Preview</h3>
                    <div class="contact-preview" id="contactPreview"></div>
                </div>
                
                <button type="submit" class="generate-btn" id="generateBtn">
                    🎯 Generate QR Code
                </button>
            </form>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Generating your QR code...</p>
            </div>
            
            <div class="error-message" id="errorMessage"></div>
            
            <div class="result-container" id="resultContainer">
                <div class="success-message">
                    ✅ QR Code generated successfully!
                </div>
                <div class="qr-code-container">
                    <img id="qrCode" class="qr-code" alt="Generated QR Code">
                </div>
                <div>
                    <button class="download-btn" id="downloadBtn">📥 Download QR Code</button>
                    <button class="share-btn" id="shareBtn">📤 Share QR Code</button>
                </div>
                <p style="margin-top: 15px; color: #666; font-size: 0.9rem;">
                    📱 Scan with any QR code reader to add contact to your phone
                </p>
            </div>
        </div>
        
        <div class="footer">
            <p>🔒 Your data is processed securely and not stored on our servers</p>
        </div>
    </div>

    <script>
        // Real-time preview update
        function updatePreview() {
            const formData = new FormData(document.getElementById('vcardForm'));
            const preview = document.getElementById('contactPreview');
            const previewSection = document.getElementById('previewSection');
            
            const firstName = formData.get('first_name');
            const lastName = formData.get('last_name');
            const phone = formData.get('phone');
            const email = formData.get('email');
            
            if (firstName || lastName || phone || email) {
                let previewHTML = '';
                if (firstName || lastName) {
                    previewHTML += `<div class="contact-item"><strong>Name:</strong> ${firstName} ${lastName}</div>`;
                }
                if (phone) {
                    previewHTML += `<div class="contact-item"><strong>Phone:</strong> ${phone}</div>`;
                }
                if (email) {
                    previewHTML += `<div class="contact-item"><strong>Email:</strong> ${email}</div>`;
                }
                if (formData.get('organization')) {
                    previewHTML += `<div class="contact-item"><strong>Company:</strong> ${formData.get('organization')}</div>`;
                }
                if (formData.get('title')) {
                    previewHTML += `<div class="contact-item"><strong>Title:</strong> ${formData.get('title')}</div>`;
                }
                if (formData.get('website')) {
                    previewHTML += `<div class="contact-item"><strong>Website:</strong> ${formData.get('website')}</div>`;
                }
                if (formData.get('address')) {
                    previewHTML += `<div class="contact-item"><strong>Address:</strong> ${formData.get('address')}</div>`;
                }
                
                preview.innerHTML = previewHTML;
                previewSection.style.display = 'block';
            } else {
                previewSection.style.display = 'none';
            }
        }
        
        // Add event listeners for real-time preview
        document.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', updatePreview);
        });
        
        // Form submission
        document.getElementById('vcardForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('generateBtn').disabled = true;
            document.getElementById('errorMessage').style.display = 'none';
            document.getElementById('resultContainer').classList.remove('show');
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // Show QR code
                    document.getElementById('qrCode').src = 'data:image/png;base64,' + result.qr_image;
                    document.getElementById('resultContainer').classList.add('show');
                    
                    // Setup download functionality
                    document.getElementById('downloadBtn').onclick = function() {
                        const link = document.createElement('a');
                        link.download = `${data.first_name}_${data.last_name}_vCard_QR.png`;
                        link.href = 'data:image/png;base64,' + result.qr_image;
                        link.click();
                    };
                    
                    // Setup share functionality (if supported)
                    document.getElementById('shareBtn').onclick = async function() {
                        if (navigator.share) {
                            try {
                                // Convert base64 to blob for sharing
                                const byteCharacters = atob(result.qr_image);
                                const byteNumbers = new Array(byteCharacters.length);
                                for (let i = 0; i < byteCharacters.length; i++) {
                                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                                }
                                const byteArray = new Uint8Array(byteNumbers);
                                const blob = new Blob([byteArray], {type: 'image/png'});
                                const file = new File([blob], `${data.first_name}_${data.last_name}_vCard_QR.png`, {type: 'image/png'});
                                
                                await navigator.share({
                                    title: 'Contact QR Code',
                                    text: `Contact QR code for ${data.first_name} ${data.last_name}`,
                                    files: [file]
                                });
                            } catch (err) {
                                console.log('Error sharing:', err);
                                // Fallback to download
                                document.getElementById('downloadBtn').click();
                            }
                        } else {
                            // Fallback to download
                            document.getElementById('downloadBtn').click();
                        }
                    };
                    
                } else {
                    // Show error
                    document.getElementById('errorMessage').textContent = result.error;
                    document.getElementById('errorMessage').style.display = 'block';
                }
                
            } catch (error) {
                document.getElementById('errorMessage').textContent = 'Network error. Please try again.';
                document.getElementById('errorMessage').style.display = 'block';
            } finally {
                // Hide loading
                document.getElementById('loading').style.display = 'none';
                document.getElementById('generateBtn').disabled = false;
            }
        });
        
        // Initialize preview
        updatePreview();
    </script>
</body>
</html>
'''

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

# Export the Flask app for Vercel
def handler(environ, start_response):
    return app(environ, start_response)

# This is the entry point for Vercel
app_instance = app

# For local development
if __name__ == '__main__':
    app.run(debug=True)
