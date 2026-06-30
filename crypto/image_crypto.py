"""
Image Encryption Module
========================

Provides AES-256-CBC encryption and decryption for raw image file bytes.
The encrypted output is raw binary (IV prepended to ciphertext), NOT
base64-encoded, making it suitable for direct file storage.

After decryption, the module optionally validates that the output is a
recognizable image format using Pillow, but always returns the raw bytes
regardless of validation outcome.

Usage:
    >>> from crypto.image_crypto import encrypt_image, decrypt_image
    >>> with open("photo.png", "rb") as f:
    ...     original = f.read()
    >>> encrypted = encrypt_image(original, "my-password")
    >>> decrypted = decrypt_image(encrypted, "my-password")
    >>> assert decrypted == original
"""

import hashlib
import logging
from io import BytesIO

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from PIL import Image

logger = logging.getLogger(__name__)


def _derive_key(password: str) -> bytes:
    """
    Derive a 32-byte AES-256 key from a password using SHA-256.

    Args:
        password: The user-supplied password string.

    Returns:
        A 32-byte key suitable for AES-256 encryption.
    """
    return hashlib.sha256(password.encode("utf-8")).digest()


def encrypt_image(image_bytes: bytes, password: str) -> bytes:
    """
    Encrypt raw image file bytes with AES-256-CBC.

    Derives a 32-byte key from the password via SHA-256, generates a
    random 16-byte IV, pads the image bytes with PKCS7, encrypts them,
    and returns the IV prepended to the ciphertext as raw binary.

    Args:
        image_bytes: The raw bytes of the image file to encrypt.
            Must be a non-empty bytes object.
        password: The password used to derive the encryption key.
            Must be a non-empty string.

    Returns:
        Raw binary bytes: IV (16 bytes) + encrypted_bytes. This is NOT
        base64-encoded.

    Raises:
        TypeError: If image_bytes is not bytes or password is not a
            string.
        ValueError: If image_bytes or password is empty.
    """
    if not isinstance(image_bytes, bytes):
        raise TypeError("Image data must be a bytes object.")
    if not isinstance(password, str):
        raise TypeError("Password must be a string.")
    if not image_bytes:
        raise ValueError("Image data cannot be empty.")
    if not password:
        raise ValueError("Password cannot be empty.")

    key = _derive_key(password)
    iv = get_random_bytes(AES.block_size)  # 16 bytes
    cipher = AES.new(key, AES.MODE_CBC, iv)

    padded_data = pad(image_bytes, AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)

    # Return IV + ciphertext as raw binary
    return iv + encrypted_data


def decrypt_image(encrypted_bytes: bytes, password: str) -> bytes:
    """
    Decrypt AES-256-CBC encrypted image bytes.

    Extracts the first 16 bytes as the IV, derives the key from the
    password via SHA-256, decrypts the remaining bytes, removes PKCS7
    padding, and returns the original image file bytes.

    After decryption, attempts to validate the output as a recognizable
    image using Pillow. If validation fails, a warning is logged but the
    raw bytes are still returned.

    Args:
        encrypted_bytes: The encrypted binary data (IV + ciphertext) as
            produced by :func:`encrypt_image`.
        password: The password used during encryption.

    Returns:
        The original image file bytes.

    Raises:
        TypeError: If encrypted_bytes is not bytes or password is not a
            string.
        ValueError: If inputs are empty, the data is corrupt, or the
            password is incorrect.
    """
    if not isinstance(encrypted_bytes, bytes):
        raise TypeError("Encrypted data must be a bytes object.")
    if not isinstance(password, str):
        raise TypeError("Password must be a string.")
    if not encrypted_bytes:
        raise ValueError("Encrypted data cannot be empty.")
    if not password:
        raise ValueError("Password cannot be empty.")

    if len(encrypted_bytes) < AES.block_size + AES.block_size:
        raise ValueError(
            "Invalid encrypted data: too short to contain an IV and at "
            "least one encrypted block."
        )

    iv = encrypted_bytes[: AES.block_size]
    ciphertext = encrypted_bytes[AES.block_size :]

    key = _derive_key(password)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    try:
        padded_data = cipher.decrypt(ciphertext)
        image_bytes = unpad(padded_data, AES.block_size)
    except (ValueError, KeyError) as exc:
        raise ValueError(
            "Decryption failed. The password may be incorrect or the "
            "encrypted data may be corrupt."
        ) from exc

    # Attempt to validate the decrypted bytes as a recognizable image
    try:
        img = Image.open(BytesIO(image_bytes))
        img.verify()
        logger.debug(
            "Decrypted image validated successfully (format=%s, size=%s).",
            img.format,
            img.size,
        )
    except Exception:
        logger.warning(
            "Decrypted data could not be verified as a valid image. "
            "Returning raw bytes anyway. The password may be incorrect "
            "or the original file may not be a standard image format."
        )

    return image_bytes
