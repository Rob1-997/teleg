from io import BytesIO
from PIL import Image




async def crop_square_bytes(
    data: bytes,
    size: int = 160,      # итоговый размер 160×160
    quality: int = 75     # JPEG-качество 0–100
) -> bytes:
    """
    Центрированная квадратная обрезка + масштаб до size×size + JPEG-сжатие.
    """
    with Image.open(BytesIO(data)) as img:
        img = img.convert("RGB")
        w, h = img.size
        m   = min(w, h)
        left   = (w - m) // 2
        top    = (h - m) // 2
        img = img.crop((left, top, left + m, top + m))
        img = img.resize((size, size), Image.LANCZOS)

        buf = BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        return buf.getvalue()