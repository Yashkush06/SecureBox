"""
AES-256-CBC Encryption Module
==============================

Provides symmetric encryption and decryption using AES-256 in CBC mode
with PKCS7 padding. Keys are derived from user-supplied passphrases via
SHA-256 hashing. Initialization vectors are generated using a
cryptographically secure random number generator.

Usage:
    >>> from crypto.aes import encrypt, decrypt
    >>> ciphertext = encrypt("Hello, World!", "my-secret-passphrase")
    >>> plaintext = decrypt(ciphertext, "my-secret-passphrase")
    >>> assert plaintext == "Hello, World!"
"""

import base64
import hashlib

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


def _derive_key(passphrase: str) -> bytes:
    """
    Derive a 32-byte AES-256 key from a passphrase using SHA-256.

    Args:
        passphrase: The user-supplied passphrase string.

    Returns:
        A 32-byte key suitable for AES-256 encryption.
    """
    return hashlib.sha256(passphrase.encode("utf-8")).digest()


def encrypt(plaintext: str, passphrase: str) -> str:
    """
    Encrypt plaintext using AES-256-CBC.

    Derives a 32-byte key from the passphrase using SHA-256, generates a
    random 16-byte initialization vector, pads the plaintext with PKCS7,
    encrypts using AES in CBC mode, and returns the result as a base64-
    encoded string containing the IV prepended to the ciphertext.

    Args:
        plaintext: The text to encrypt. Must be a non-empty string.
        passphrase: The passphrase used to derive the encryption key.
            Must be a non-empty string.

    Returns:
        A base64-encoded string of the form base64(IV + ciphertext).

    Raises:
        TypeError: If plaintext or passphrase is not a string.
        ValueError: If plaintext or passphrase is empty.
    """
    if not isinstance(plaintext, str):
        raise TypeError("Plaintext must be a string.")
    if not isinstance(passphrase, str):
        raise TypeError("Passphrase must be a string.")
    if not plaintext:
        raise ValueError("Plaintext cannot be empty.")
    if not passphrase:
        raise ValueError("Passphrase cannot be empty.")

    key = _derive_key(passphrase)
    iv = get_random_bytes(AES.block_size)  # 16 bytes
    cipher = AES.new(key, AES.MODE_CBC, iv)

    plaintext_bytes = plaintext.encode("utf-8")
    padded_data = pad(plaintext_bytes, AES.block_size)
    ciphertext = cipher.encrypt(padded_data)

    # Prepend IV to ciphertext and base64 encode the combined result
    combined = iv + ciphertext
    return base64.b64encode(combined).decode("utf-8")


def decrypt(ciphertext_b64: str, passphrase: str) -> str:
    """
    Decrypt AES-256-CBC encrypted text.

    Derives the 32-byte key from the passphrase using SHA-256, base64-
    decodes the input, extracts the first 16 bytes as the IV, decrypts
    the remaining bytes using AES-CBC, removes PKCS7 padding, and returns
    the original plaintext.

    Args:
        ciphertext_b64: The base64-encoded ciphertext (IV + ciphertext).
        passphrase: The passphrase used during encryption.

    Returns:
        The decrypted plaintext as a UTF-8 string.

    Raises:
        TypeError: If ciphertext_b64 or passphrase is not a string.
        ValueError: If inputs are empty, the data is corrupt, or the
            passphrase is incorrect.
    """
    if not isinstance(ciphertext_b64, str):
        raise TypeError("Ciphertext must be a base64-encoded string.")
    if not isinstance(passphrase, str):
        raise TypeError("Passphrase must be a string.")
    if not ciphertext_b64:
        raise ValueError("Ciphertext cannot be empty.")
    if not passphrase:
        raise ValueError("Passphrase cannot be empty.")

    try:
        raw = base64.b64decode(ciphertext_b64)
    except Exception as exc:
        raise ValueError(
            "Invalid ciphertext: the data is not valid base64."
        ) from exc

    if len(raw) < AES.block_size + AES.block_size:
        raise ValueError(
            "Invalid ciphertext: data is too short to contain an IV "
            "and at least one encrypted block."
        )

    iv = raw[: AES.block_size]
    ciphertext = raw[AES.block_size :]

    key = _derive_key(passphrase)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    try:
        padded_plaintext = cipher.decrypt(ciphertext)
        plaintext_bytes = unpad(padded_plaintext, AES.block_size)
    except (ValueError, KeyError) as exc:
        raise ValueError(
            "Decryption failed. The passphrase may be incorrect or the "
            "data may be corrupt."
        ) from exc

    try:
        return plaintext_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "Decryption produced invalid UTF-8 data. The passphrase is "
            "likely incorrect."
        ) from exc
