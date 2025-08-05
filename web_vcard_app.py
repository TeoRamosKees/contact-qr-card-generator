from flask import Flask, render_template, request, send_file, jsonify
import qrcode
from PIL import Image
import io
import base64
import os
from datetime import datetime

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
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
        
        # Generate filename
        filename = f"{data.get('first_name', 'contact').strip()}_{data.get('last_name', 'card').strip()}_qr.png".replace(' ', '_')
        
        return jsonify({
            'success': True,
            'qr_image': img_base64,
            'filename': filename,
            'vcard_content': vcard
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Error generating QR code: {str(e)}"
        })

@app.route('/download/<filename>')
def download_qr(filename):
    """Handle QR code download"""
    try:
        # This would need to be implemented with session storage
        # For now, return a basic response
        return jsonify({'message': 'Download functionality would be implemented here'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    print("🌐 vCard QR Generator Web App")
    print("📱 Perfect for iOS, Android, and all devices!")
    print("🚀 Starting server...")
    print("📡 Access from any device on your network at:")
    print("   • Local: http://localhost:5000")
    print("   • Network: http://[your-ip]:5000")
    print("💡 To find your IP: ipconfig (Windows) or ifconfig (Mac/Linux)")
    app.run(debug=True, host='0.0.0.0', port=5000)
