"""
SecureBox — Flask Application Server
=====================================

Server-rendered cybersecurity web application using Jinja2 templates.
All forms submit via POST; pages re-render with results (no SPA / no JSON API).

Routes:
    /           — Landing page
    /text       — Text encryption & decryption (AES, DES, RSA)
    /image      — Image encryption & decryption
    /image/download/<filename> — Secure file download
    /qr         — QR code generation with encrypted data
    /compare    — Side-by-side algorithm comparison
    /about      — About page
"""

import os
import uuid
import base64
import time
from io import BytesIO

from flask import Flask, render_template, request, send_file, abort
from PIL import Image

from crypto import aes, des, rsa
from crypto import image_crypto, qr_generator

# ---------------------------------------------------------------------------
# App initialisation
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.urandom(32)

# Upload directory for temporary files (encrypted images, etc.)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB max upload


# ---------------------------------------------------------------------------
# Route 1 — Landing Page
# ---------------------------------------------------------------------------

@app.route('/')
def landing():
    """Render the marketing / landing page."""
    return render_template('landing.html')


# ---------------------------------------------------------------------------
# Route 2 — Text Encryption (AES / DES / RSA)
# ---------------------------------------------------------------------------

@app.route('/text', methods=['GET', 'POST'])
def text_page():
    """Encrypt or decrypt text using AES-256, DES, or RSA-2048.

    Template variables (all strings):
        algorithm, plaintext, ciphertext, key,
        public_key, private_key, error, success
    """
    # Context dict — every key the template expects
    ctx = {
        'algorithm': request.form.get('algorithm', 'aes'),
        'plaintext': '',
        'ciphertext': '',
        'key': '',
        'public_key': '',
        'private_key': '',
        'error': '',
        'success': '',
    }

    if request.method == 'POST':
        action = request.form.get('action', '')
        algorithm = request.form.get('algorithm', 'aes')
        plaintext = request.form.get('plaintext', '').strip()
        ciphertext = request.form.get('ciphertext', '').strip()
        key = request.form.get('key', '').strip()
        public_key = request.form.get('public_key', '').strip()
        private_key = request.form.get('private_key', '').strip()

        # Preserve all form values so the user doesn't lose input
        ctx.update({
            'algorithm': algorithm,
            'plaintext': plaintext,
            'ciphertext': ciphertext,
            'key': key,
            'public_key': public_key,
            'private_key': private_key,
        })

        try:
            # --- Generate RSA key pair ---
            if action == 'generate_keys':
                pub, priv = rsa.generate_keys()
                ctx['public_key'] = pub
                ctx['private_key'] = priv
                ctx['success'] = 'RSA key pair generated successfully!'

            # --- Encrypt ---
            elif action == 'encrypt':
                plain_input = plaintext if plaintext else ciphertext
                if not plain_input:
                    ctx['error'] = 'Please enter text to encrypt.'
                elif algorithm == 'rsa':
                    if not public_key:
                        ctx['error'] = (
                            'Public key is required for RSA encryption. '
                            'Generate or upload one.'
                        )
                    else:
                        result = rsa.encrypt(plain_input, public_key)
                        ctx['ciphertext'] = result
                        ctx['plaintext'] = plain_input
                        ctx['success'] = 'Text encrypted successfully with RSA!'
                elif algorithm in ('aes', 'des'):
                    if not key:
                        ctx['error'] = 'Please enter a secret key.'
                    else:
                        module = aes if algorithm == 'aes' else des
                        result = module.encrypt(plain_input, key)
                        ctx['ciphertext'] = result
                        ctx['plaintext'] = plain_input
                        ctx['success'] = (
                            f'Text encrypted successfully with {algorithm.upper()}!'
                        )

            # --- Decrypt ---
            elif action == 'decrypt':
                cipher_input = ciphertext if ciphertext else plaintext
                if not cipher_input:
                    ctx['error'] = 'Please enter ciphertext to decrypt.'
                elif algorithm == 'rsa':
                    if not private_key:
                        ctx['error'] = 'Private key is required for RSA decryption.'
                    else:
                        result = rsa.decrypt(cipher_input, private_key)
                        ctx['plaintext'] = result
                        ctx['ciphertext'] = cipher_input
                        ctx['success'] = 'Text decrypted successfully with RSA!'
                elif algorithm in ('aes', 'des'):
                    if not key:
                        ctx['error'] = (
                            'Please enter the secret key used for encryption.'
                        )
                    else:
                        module = aes if algorithm == 'aes' else des
                        result = module.decrypt(cipher_input, key)
                        ctx['plaintext'] = result
                        ctx['ciphertext'] = cipher_input
                        ctx['success'] = (
                            f'Text decrypted successfully with {algorithm.upper()}!'
                        )

        except Exception as e:
            ctx['error'] = str(e)

    return render_template('text.html', active_page='text', **ctx)


# ---------------------------------------------------------------------------
# Route 3 — Image Encryption / Decryption
# ---------------------------------------------------------------------------

@app.route('/image', methods=['GET', 'POST'])
def image_page():
    """Encrypt an image file or decrypt a previously-encrypted `.enc` file.

    Memory-only processing: does not write files to disk, supporting serverless
    platforms like Vercel. Downloads are served via client-side base64 Data URLs.
    """
    ctx = {
        'error': '',
        'success': '',
        'encrypted_b64': '',
        'decrypted_b64': '',
        'image_preview': '',
        'action': 'encrypt',
        'ext': 'png',
        'mime': 'image/png'
    }

    if request.method == 'POST':
        action = request.form.get('action', 'encrypt')
        password = request.form.get('password', '').strip()
        file = request.files.get('file')
        ctx['action'] = action

        # --- Input validation ---
        if not file or file.filename == '':
            ctx['error'] = 'Please select a file to upload.'
        elif not password:
            ctx['error'] = 'Please enter a password.'
        else:
            try:
                file_bytes = file.read()

                if action == 'encrypt':
                    # Only allow common image formats
                    allowed = {'png', 'jpg', 'jpeg'}
                    ext = (
                        file.filename.rsplit('.', 1)[-1].lower()
                        if '.' in file.filename
                        else 'png'
                    )
                    if ext not in allowed:
                        ctx['error'] = (
                            'Only PNG, JPG, and JPEG images are supported.'
                        )
                    else:
                        encrypted = image_crypto.encrypt_image(file_bytes, password)
                        ctx['encrypted_b64'] = base64.b64encode(encrypted).decode('utf-8')
                        ctx['success'] = (
                            'Image encrypted successfully! Click download to save.'
                        )

                elif action == 'decrypt':
                    decrypted = image_crypto.decrypt_image(file_bytes, password)
                    # Validate the decrypted bytes are a real image
                    img = Image.open(BytesIO(decrypted))
                    fmt = img.format or 'PNG'
                    ext = fmt.lower()
                    if ext == 'jpeg':
                        ext = 'jpg'

                    decrypted_b64 = base64.b64encode(decrypted).decode('utf-8')
                    mime = f'image/{fmt.lower()}'
                    ctx['decrypted_b64'] = decrypted_b64
                    ctx['ext'] = ext
                    ctx['mime'] = mime
                    ctx['image_preview'] = f'data:{mime};base64,{decrypted_b64}'
                    ctx['success'] = 'Image decrypted successfully!'

            except Exception as e:
                ctx['error'] = str(e)

    return render_template('image.html', active_page='image', **ctx)


# ---------------------------------------------------------------------------
# Route 5 — QR Code Encryption
# ---------------------------------------------------------------------------

@app.route('/qr', methods=['GET', 'POST'])
def qr_page():
    """Encrypt text, encode it into a QR code, or decode / decrypt from a QR.

    Template variables:
        algorithm, plaintext, key, ciphertext, qr_image,
        decoded_text, decrypted_text, error, success, action
    """
    ctx = {
        'algorithm': 'aes',
        'plaintext': '',
        'key': '',
        'ciphertext': '',
        'qr_image': '',
        'decoded_text': '',
        'decrypted_text': '',
        'error': '',
        'success': '',
        'action': '',
    }

    if request.method == 'POST':
        action = request.form.get('action', '')
        ctx['action'] = action
        ctx['algorithm'] = request.form.get('algorithm', 'aes')
        ctx['plaintext'] = request.form.get('plaintext', '').strip()
        ctx['key'] = request.form.get('key', '').strip()
        ctx['ciphertext'] = request.form.get('ciphertext', '').strip()

        try:
            # --- Generate: encrypt text → QR code ---
            if action == 'generate':
                plaintext = ctx['plaintext']
                algorithm = ctx['algorithm']
                key = ctx['key']

                if not plaintext:
                    ctx['error'] = 'Please enter text to encrypt.'
                elif not key:
                    ctx['error'] = 'Please enter a secret key.'
                else:
                    # Encrypt with the chosen algorithm
                    if algorithm == 'aes':
                        encrypted = aes.encrypt(plaintext, key)
                    elif algorithm == 'des':
                        encrypted = des.encrypt(plaintext, key)
                    else:
                        # RSA — generate a fresh key pair and encrypt
                        pub, priv = rsa.generate_keys()
                        encrypted = rsa.encrypt(plaintext, pub)
                        ctx['ciphertext'] = encrypted

                    ctx['ciphertext'] = encrypted

                    # Render the encrypted text as a QR PNG
                    qr_bytes = qr_generator.generate_qr(encrypted)
                    qr_b64 = base64.b64encode(qr_bytes).decode('utf-8')
                    ctx['qr_image'] = f'data:image/png;base64,{qr_b64}'
                    ctx['success'] = 'QR code generated with encrypted data!'

            # --- Decode: extract text from a QR image ---
            elif action == 'decode':
                qr_file = request.files.get('qr_file')
                if not qr_file or qr_file.filename == '':
                    ctx['error'] = 'Please upload a QR code image.'
                else:
                    qr_bytes = qr_file.read()
                    decoded = qr_generator.decode_qr(qr_bytes)
                    ctx['decoded_text'] = decoded
                    ctx['ciphertext'] = decoded
                    ctx['success'] = (
                        'QR code decoded! The encrypted text has been extracted.'
                    )

            # --- Decrypt: decrypt the extracted ciphertext ---
            elif action == 'decrypt':
                ciphertext = ctx['ciphertext']
                algorithm = ctx['algorithm']
                key = ctx['key']

                if not ciphertext:
                    ctx['error'] = 'No ciphertext to decrypt.'
                elif not key:
                    ctx['error'] = 'Please enter the decryption key.'
                else:
                    if algorithm == 'aes':
                        result = aes.decrypt(ciphertext, key)
                    elif algorithm == 'des':
                        result = des.decrypt(ciphertext, key)
                    else:
                        ctx['error'] = (
                            'RSA decryption requires a private key. '
                            'Use the Text Encryption page for RSA.'
                        )
                        result = None

                    if result:
                        ctx['decrypted_text'] = result
                        ctx['success'] = 'Text decrypted successfully!'

        except Exception as e:
            ctx['error'] = str(e)

    return render_template('qr.html', active_page='qr', **ctx)


# ---------------------------------------------------------------------------
# Route 6 — Algorithm Comparison
# ---------------------------------------------------------------------------

@app.route('/compare', methods=['GET', 'POST'])
def compare_page():
    """Encrypt the same plaintext with AES, DES, and RSA side-by-side.

    Measures wall-clock time and displays cipher metadata so the user can
    compare speed, output size, and security level.

    Template variables:
        results (list[dict]), plaintext, key, error, success
    """
    ctx = {
        'results': [],
        'plaintext': '',
        'key': '',
        'error': '',
        'success': '',
    }

    if request.method == 'POST':
        plaintext = request.form.get('plaintext', '').strip()
        key = request.form.get('key', '').strip()
        ctx['plaintext'] = plaintext
        ctx['key'] = key

        if not plaintext:
            ctx['error'] = 'Please enter text to compare.'
        elif not key:
            ctx['error'] = 'Please enter a secret key.'
        else:
            results = []

            # ---- AES-256 ----
            try:
                start = time.perf_counter()
                aes_cipher = aes.encrypt(plaintext, key)
                aes_time = (time.perf_counter() - start) * 1000
                results.append({
                    'name': 'AES-256',
                    'time_ms': round(aes_time, 4),
                    'ciphertext': aes_cipher,
                    'ciphertext_length': len(aes_cipher),
                    'key_size': '256 bits',
                    'type': 'Symmetric',
                    'security_level': 'Very High',
                    'security_color': 'success',
                })
            except Exception as e:
                results.append({'name': 'AES-256', 'error': str(e)})

            # ---- DES ----
            try:
                start = time.perf_counter()
                des_cipher = des.encrypt(plaintext, key)
                des_time = (time.perf_counter() - start) * 1000
                results.append({
                    'name': 'DES',
                    'time_ms': round(des_time, 4),
                    'ciphertext': des_cipher,
                    'ciphertext_length': len(des_cipher),
                    'key_size': '56 bits',
                    'type': 'Symmetric',
                    'security_level': 'Low',
                    'security_color': 'warning',
                })
            except Exception as e:
                results.append({'name': 'DES', 'error': str(e)})

            # ---- RSA-2048 ----
            try:
                pub, priv = rsa.generate_keys()
                start = time.perf_counter()
                rsa_cipher = rsa.encrypt(plaintext, pub)
                rsa_time = (time.perf_counter() - start) * 1000
                results.append({
                    'name': 'RSA-2048',
                    'time_ms': round(rsa_time, 4),
                    'ciphertext': rsa_cipher,
                    'ciphertext_length': len(rsa_cipher),
                    'key_size': '2048 bits',
                    'type': 'Asymmetric',
                    'security_level': 'High',
                    'security_color': 'primary',
                })
            except Exception as e:
                results.append({'name': 'RSA-2048', 'error': str(e)})

            ctx['results'] = results
            ctx['success'] = 'Comparison complete!'

    return render_template('compare.html', active_page='compare', **ctx)


# ---------------------------------------------------------------------------
# Route 7 — About Page
# ---------------------------------------------------------------------------

@app.route('/about')
def about_page():
    """Render the static about / information page."""
    return render_template('about.html', active_page='about')


# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------

@app.errorhandler(413)
def too_large(e):
    """Handle file-upload size limit exceeded."""
    return render_template(
        'base_error.html',
        error='File too large. Maximum size is 10 MB.',
        code=413,
    ), 413


@app.errorhandler(404)
def not_found(e):
    """Handle missing pages / resources."""
    return render_template(
        'base_error.html',
        error='Page not found.',
        code=404,
    ), 404


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
