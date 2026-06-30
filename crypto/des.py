"""
DES-CBC Encryption Module
==========================

Provides symmetric encryption and decryption using DES in CBC mode
with PKCS7 padding. Keys are derived from user-supplied passphrases by
taking the first 8 bytes of the SHA-256 hash. Initialization vectors are
generated using a cryptographically secure random number generator.

.. warning::
    DES is considered cryptographically weak and should only be used for
    educational or legacy compatibility purposes. For production use,
    prefer AES-256 (see :mod:`crypto.aes`).

Usage:
    >>> from crypto.des import encrypt, decrypt
    >>> ciphertext = encrypt("Hello, World!", "my-secret-passphrase")
    >>> plaintext = decrypt(ciphertext, "my-secret-passphrase")
    >>> assert plaintext == "Hello, World!"
"""

import base64
import hashlib

from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


def _derive_key(passphrase: str) -> bytes:
    """
    Derive an 8-byte DES key from a passphrase.

    Uses SHA-256 to hash the passphrase and takes the first 8 bytes
    of the resulting digest as the DES key.

    Args:
        passphrase: The user-supplied passphrase string.

    Returns:
        An 8-byte key suitable for DES encryption.
    """
    return hashlib.sha256(passphrase.encode("utf-8")).digest()[:8]


def encrypt(plaintext: str, passphrase: str) -> str:
    """
    Encrypt plaintext using DES-CBC.

    Derives an 8-byte key from the passphrase (first 8 bytes of its
    SHA-256 hash), generates a random 8-byte initialization vector,
    pads the plaintext with PKCS7, encrypts using DES in CBC mode, and
    returns the result as a base64-encoded string.

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
    iv = get_random_bytes(DES.block_size)  # 8 bytes
    cipher = DES.new(key, DES.MODE_CBC, iv)

    plaintext_bytes = plaintext.encode("utf-8")
    padded_data = pad(plaintext_bytes, DES.block_size)
    ciphertext = cipher.encrypt(padded_data)

    # Prepend IV to ciphertext and base64 encode the combined result
    combined = iv + ciphertext
    return base64.b64encode(combined).decode("utf-8")


def decrypt(ciphertext_b64: str, passphrase: str) -> str:
    """
    Decrypt DES-CBC encrypted text.

    Derives the 8-byte key from the passphrase, base64-decodes the
    input, extracts the first 8 bytes as the IV, decrypts the remaining
    bytes using DES-CBC, removes PKCS7 padding, and returns the original
    plaintext.

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

    if len(raw) < DES.block_size + DES.block_size:
        raise ValueError(
            "Invalid ciphertext: data is too short to contain an IV "
            "and at least one encrypted block."
        )

    iv = raw[: DES.block_size]
    ciphertext = raw[DES.block_size :]

    key = _derive_key(passphrase)
    cipher = DES.new(key, DES.MODE_CBC, iv)

    try:
        padded_plaintext = cipher.decrypt(ciphertext)
        plaintext_bytes = unpad(padded_plaintext, DES.block_size)
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
