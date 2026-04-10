# Secure Cookie and Digital Signature System

A comprehensive security demonstration project built with **Python Flask** that implements cryptographic techniques to ensure data integrity and authenticity. This project covers secure cookie management, RSA digital signatures, and simulations of common cryptographic attacks.

## 🚀 Features

### Part A: Cookie Protection using MAC
*   **Authentication Mechanism:** A login system that generates secure session cookies.
*   **HMAC (SHA-256):** Implementation of Message Authentication Code to protect cookie content from tampering.
*   **Tampering Detection:** The server re-calculates the MAC on each request to verify data integrity.
*   **Self-Correction:** If tampering is detected (e.g., role change from `user` to `admin`), the system automatically resets the user's role and notifies the user.
*   **Session Expiration:** Implementation of expiration timestamps to prevent replay attacks.

### Part B: Digital Signature Module
*   **RSA Key Generation:** Generates 2048-bit RSA Public/Private key pairs.
*   **File/Text Signing:** Sign any content using a Private Key and SHA-256 hashing.
*   **Integrity Verification:** Validate the authenticity of the signed content using the corresponding Public Key.
*   **Visual Proof:** Demonstrates how changing a single character in the message leads to a verification failure.

### 🛡️ Bonus Tasks (Cryptographic Attacks)
Based on the discussion in **Wong (Page 150)**, this system demonstrates:
1.  **Key Substitution Attack:** Simulates an attacker replacing the server's Public Key in the database to make malicious signatures appear valid.
2.  **Message Key Substitution Attack:** Demonstrates the vulnerability of trusting an unvetted public key provided alongside a message (Self-signed attack).

## 📁 Project Structure

```text
├── app.py                 # Main Flask application and business logic
├── crypto_helpers.py      # Cryptographic utility functions (HMAC, RSA)
├── requirements.txt       # List of required Python libraries
└── templates/             # UI Components (HTML/CSS)
    ├── login.html
    ├── dashboard.html
    ├── signatures.html
    └── attacks.html
