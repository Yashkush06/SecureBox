# 🔐 SecureBox

> A modern web application for encrypting text, images, and QR codes using industry-standard cryptographic algorithms.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-Framework-black)
![HTML](https://img.shields.io/badge/HTML5-E34F26)
![CSS](https://img.shields.io/badge/CSS3-1572B6)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-F7DF1E)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📖 Overview

SecureBox is a clean and modern web application built with **Flask, HTML, CSS, and JavaScript** that demonstrates the fundamentals of cryptography through an interactive interface.

It allows users to encrypt and decrypt text, securely encrypt image files, generate encrypted QR codes, and compare the characteristics of different encryption algorithms.

The project was built for educational purposes to understand how modern encryption techniques work in real-world applications.

---

## ✨ Features

### 🔐 Text Encryption
- AES Encryption
- DES Encryption
- RSA Encryption
- Encrypt & Decrypt text
- Copy encrypted text
- Download encrypted output

### 🖼️ Image Encryption
- Upload image
- AES-256 image encryption
- Download encrypted `.enc` file
- Decrypt back to original image
- Image preview

### 📱 QR Code Encryption
- Encrypt text
- Generate QR Code
- Download QR Code
- Scan QR
- Decrypt scanned data

### 📊 Algorithm Comparison
Compare:

- AES
- DES
- RSA

Displays:

- Encryption Type
- Key Size
- Encryption Speed
- Ciphertext Size
- Security Level

---

## 🛠 Tech Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Flask

### Libraries
- PyCryptodome
- Cryptography
- Pillow
- QRCode

---

## 📂 Project Structure

```text
SecureBox/
│
├── app.py
├── requirements.txt
│
├── templates/
├── static/
├── crypto/
└── README.md
```

---

## 🚀 Installation

Clone the repository

```bash
git clone https://github.com/Yashkush06/SecureBox.git
```

Move into the project

```bash
cd SecureBox
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the environment

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python app.py
```

Open your browser

```
http://127.0.0.1:5000
```

---

## 📸 Screenshots

### Landing Page

*(Add screenshot here)*

---

### Text Encryption

*(Add screenshot here)*

---

### Image Encryption

*(Add screenshot here)*

---

### QR Encryption

*(Add screenshot here)*

---

### Compare Algorithms

*(Add screenshot here)*

---

## 🔒 Algorithms Used

### AES
- Symmetric Encryption
- 256-bit Key
- Fast
- Industry Standard

### DES
- Symmetric Encryption
- 56-bit Key
- Included for educational purposes

### RSA
- Asymmetric Encryption
- Public & Private Keys
- Secure key exchange

---

## 📚 What I Learned

- Symmetric vs Asymmetric Encryption
- AES, DES and RSA implementation
- Image encryption using byte-level encryption
- QR Code generation
- Flask backend development
- Secure handling of cryptographic keys
- Clean UI/UX design principles

---

## ⚠️ Disclaimer

This project is intended for **educational and demonstration purposes**.

DES is included only to demonstrate older encryption techniques and should **not** be used in production systems.

RSA keys are generated on demand and are not stored on the server.

---

## 🚧 Future Improvements

- User Authentication
- File Encryption
- Digital Signatures
- AES-GCM Support
- Secure Key Storage
- Drag & Drop Uploads
- API Support
- Dark/Light Theme Toggle

---

## 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

Feel free to fork the repository and submit a pull request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨💻 Author

**Yash Kushwah**

- LinkedIn: https://linkedin.com/in/yash-kushwah
- GitHub: https://github.com/Yashkush06

---

⭐ If you found this project helpful, consider giving it a star!
