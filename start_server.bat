@echo off
echo.
echo ================================================
echo        vCard QR Generator - iOS Compatible
echo ================================================
echo.
echo Starting web server for iOS devices...
echo Your friend can access this from their iPhone/iPad!
echo.
echo Installing dependencies...
pip install flask qrcode[pil] Pillow
echo.
echo Starting server...
python web_vcard_app.py
pause
