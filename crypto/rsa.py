"""
RSA-2048 Encryption Module
===========================

Provides asymmetric encryption and decryption using RSA-2048 with
PKCS#1 OAEP padding. Includes key pair generation, encryption with
a public key, and decryption with a private key.

RSA-2048 with OAEP (SHA-1 hash, MGF1) can encrypt a maximum of
approximately 190 bytes of plaintext per operation. For larger data,
use hybrid encryption (RSA to encrypt a symmetric key, then AES for
the actual data).

Usage:
    >>> from crypto.rsa import generate_keys, encrypt, decrypt
    >>> pub_pem, priv_pem = generate_keys()
    >>> ciphertext = encrypt("Hello, World!", pub_pem)
    >>> plaintext = decrypt(ciphertext, priv_pem)
    >>> assert plaintext == "Hello, World!"
"""

import base64

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

# Maximum plaintext size for RSA-2048 with OAEP (SHA-1 + MGF1):
# 256 bytes (key size) - 2 * 20 bytes (SHA-1 hash) - 2 bytes = 214 bytes
# Using a conservative limit for safety.
_RSA_MAX_PLAINTEXT_BYTES = 190


def generate_keys() -> tuple:
    """
    Generate an RSA-2048 key pair.

    Generates a 2048-bit RSA key pair and exports both keys in PEM
    format. The public key uses PKCS#8 / SubjectPublicKeyInfo format
    and the private key uses PKCS#8 format.

    Returns:
        A tuple of (public_key_pem, private_key_pem) where both values
        are PEM-encoded strings.

    Example:
        >>> pub_pem, priv_pem = generate_keys()
        >>> assert pub_pem.startswith("-----BEGIN PUBLIC KEY-----")
        >>> assert priv_pem.startswith("-----BEGIN RSA PRIVATE KEY-----")
    """
    key = RSA.generate(2048)
    private_key_pem = key.export_key("PEM").decode("utf-8")
    public_key_pem = key.publickey().export_key("PEM").decode("utf-8")
    return public_key_pem, private_key_pem


def encrypt(plaintext: str, public_key_pem: str) -> str:
    """
    Encrypt plaintext with an RSA public key using PKCS#1 OAEP.

    Imports the public key from a PEM string, encrypts the plaintext
    using PKCS#1 OAEP padding, and returns the ciphertext as a base64-
    encoded string.

    Args:
        plaintext: The text to encrypt. Must not exceed ~190 bytes when
            encoded as UTF-8 (RSA-2048 OAEP limit).
        public_key_pem: The RSA public key in PEM format.

    Returns:
        A base64-encoded ciphertext string.

    Raises:
        TypeError: If plaintext or public_key_pem is not a string.
        ValueError: If plaintext is empty, exceeds the RSA size limit,
            or the public key is invalid.
    """
    if not isinstance(plaintext, str):
        raise TypeError("Plaintext must be a string.")
    if not isinstance(public_key_pem, str):
        raise TypeError("Public key must be a PEM-encoded string.")
    if not plaintext:
        raise ValueError("Plaintext cannot be empty.")
    if not public_key_pem.strip():
        raise ValueError("Public key PEM cannot be empty.")

    plaintext_bytes = plaintext.encode("utf-8")

    if len(plaintext_bytes) > _RSA_MAX_PLAINTEXT_BYTES:
        raise ValueError(
            f"Plaintext is too long for RSA-2048 encryption. "
            f"Maximum size is {_RSA_MAX_PLAINTEXT_BYTES} bytes, but the "
            f"input is {len(plaintext_bytes)} bytes. Consider using "
            f"AES-256 for large data or a hybrid encryption scheme."
        )

    try:
        public_key = RSA.import_key(public_key_pem)
    except (ValueError, IndexError, TypeError) as exc:
        raise ValueError(
            "Invalid public key: the PEM data could not be parsed. "
            "Ensure the key is a valid RSA public key in PEM format."
        ) from exc

    cipher = PKCS1_OAEP.new(public_key)
    ciphertext = cipher.encrypt(plaintext_bytes)
    return base64.b64encode(ciphertext).decode("utf-8")


def decrypt(ciphertext_b64: str, private_key_pem: str) -> str:
    """
    Decrypt RSA ciphertext with a private key using PKCS#1 OAEP.

    Imports the private key from a PEM string, base64-decodes the
    ciphertext, decrypts using PKCS#1 OAEP, and returns the original
    plaintext.

    Args:
        ciphertext_b64: The base64-encoded ciphertext produced by
            :func:`encrypt`.
        private_key_pem: The RSA private key in PEM format.

    Returns:
        The decrypted plaintext as a UTF-8 string.

    Raises:
        TypeError: If ciphertext_b64 or private_key_pem is not a string.
        ValueError: If inputs are empty, the ciphertext is corrupt, or
            the private key does not match the public key used for
            encryption.
    """
    if not isinstance(ciphertext_b64, str):
        raise TypeError("Ciphertext must be a base64-encoded string.")
    if not isinstance(private_key_pem, str):
        raise TypeError("Private key must be a PEM-encoded string.")
    if not ciphertext_b64:
        raise ValueError("Ciphertext cannot be empty.")
    if not private_key_pem.strip():
        raise ValueError("Private key PEM cannot be empty.")

    try:
        raw_ciphertext = base64.b64decode(ciphertext_b64)
    except Exception as exc:
        raise ValueError(
            "Invalid ciphertext: the data is not valid base64."
        ) from exc

    try:
        private_key = RSA.import_key(private_key_pem)
    except (ValueError, IndexError, TypeError) as exc:
        raise ValueError(
            "Invalid private key: the PEM data could not be parsed. "
            "Ensure the key is a valid RSA private key in PEM format."
        ) from exc

    cipher = PKCS1_OAEP.new(private_key)

    try:
        plaintext_bytes = cipher.decrypt(raw_ciphertext)
    except (ValueError, TypeError) as exc:
        raise ValueError(
            "Decryption failed. The private key may not match the public "
            "key used for encryption, or the ciphertext may be corrupt."
        ) from exc

    try:
        return plaintext_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "Decryption produced invalid UTF-8 data. The key pair may "
            "be mismatched."
        ) from exc
