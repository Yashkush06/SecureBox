"""
QR Code Generation and Decoding Module
========================================

Provides utilities for generating QR code images from text data and
decoding QR codes from image bytes.

Generation uses the ``qrcode`` library with Pillow as the image backend.
Decoding uses ``pyzbar`` when available, which requires the ZBar shared
library to be installed on the system.

Usage:
    >>> from crypto.qr_generator import generate_qr, decode_qr
    >>> png_bytes = generate_qr("https://example.com")
    >>> decoded_text = decode_qr(png_bytes)
    >>> assert decoded_text == "https://example.com"
"""

from io import BytesIO

import qrcode
from PIL import Image

# Attempt to import pyzbar at module level for availability checking
_PYZBAR_AVAILABLE = True
_PYZBAR_IMPORT_ERROR = None

try:
    from pyzbar.pyzbar import decode as pyzbar_decode
except ImportError as _exc:
    _PYZBAR_AVAILABLE = False
    _PYZBAR_IMPORT_ERROR = str(_exc)
    pyzbar_decode = None  # type: ignore[assignment]


def generate_qr(data: str) -> bytes:
    """
    Generate a QR code image from text data.

    Creates a QR code using the ``qrcode`` library with the Pillow
    image factory. The QR code auto-fits to the smallest version that
    can accommodate the data.

    Args:
        data: The text data to encode in the QR code. Must be a
            non-empty string.

    Returns:
        PNG image bytes of the generated QR code.

    Raises:
        TypeError: If data is not a string.
        ValueError: If data is empty or too large for a QR code.
    """
    if not isinstance(data, str):
        raise TypeError("Data must be a string.")
    if not data:
        raise ValueError("Data cannot be empty.")

    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.getvalue()

    except (qrcode.exceptions.DataOverflowError, OverflowError) as exc:
        raise ValueError(
            "Data is too large to fit in a QR code. Try reducing the "
            "length of the input text."
        ) from exc
    except Exception as exc:
        raise ValueError(
            f"Failed to generate QR code: {exc}"
        ) from exc


def decode_qr(image_bytes: bytes) -> str:
    """
    Decode a QR code from image bytes.

    Opens the image using Pillow, converts it to grayscale, and decodes
    it using the ``pyzbar`` library. Returns the decoded text data from
    the first QR code found in the image.

    Args:
        image_bytes: Raw bytes of an image file containing a QR code.
            Must be a non-empty bytes object in a format supported by
            Pillow (PNG, JPEG, BMP, etc.).

    Returns:
        The decoded text data from the QR code.

    Raises:
        TypeError: If image_bytes is not a bytes object.
        ValueError: If image_bytes is empty, the image cannot be opened,
            or no QR code is found in the image.
        ImportError: If ``pyzbar`` is not installed or the ZBar shared
            library is not available.
    """
    if not isinstance(image_bytes, bytes):
        raise TypeError("Image data must be a bytes object.")
    if not image_bytes:
        raise ValueError("Image data cannot be empty.")

    if not _PYZBAR_AVAILABLE:
        raise ImportError(
            "The 'pyzbar' library is required for QR code decoding but "
            "could not be imported. Please install it with: "
            "pip install pyzbar\n"
            "On Linux, you may also need: sudo apt-get install libzbar0\n"
            "On macOS: brew install zbar\n"
            f"Original error: {_PYZBAR_IMPORT_ERROR}"
        )

    try:
        img = Image.open(BytesIO(image_bytes))
    except Exception as exc:
        raise ValueError(
            "Failed to open the image. Ensure the data is a valid image "
            "file (PNG, JPEG, BMP, etc.)."
        ) from exc

    # Convert to grayscale for more reliable decoding
    grayscale_img = img.convert("L")

    try:
        decoded_objects = pyzbar_decode(grayscale_img)
    except Exception as exc:
        raise ValueError(
            f"QR code decoding failed: {exc}. Ensure the image contains "
            f"a clear, readable QR code."
        ) from exc

    if not decoded_objects:
        raise ValueError(
            "No QR code found in the image. Ensure the image contains a "
            "valid, clearly visible QR code."
        )

    # Return the data from the first decoded QR code
    raw_data = decoded_objects[0].data
    if isinstance(raw_data, bytes):
        return raw_data.decode("utf-8")
    return str(raw_data)
