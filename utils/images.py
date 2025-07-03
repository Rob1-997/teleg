from io import BytesIO
from PIL import Image




async def crop_square_bytes(
    data: bytes,
    size: int = 800,        # размер итогового квадрата
    quality: int = 95        # качество JPEG (0-100)
) -> bytes:
    """
    Центрированная квадратная обрезка + уменьшение до size×size,
    сохранение в JPEG с заданным quality.
    """
    with Image.open(BytesIO(data)) as img:
        img = img.convert("RGB")
        w, h = img.size
        m = min(w, h)

        # Центрированная обрезка до квадрата
        left = (w - m) // 2
        top = (h - m) // 2
        img = img.crop((left, top, left + m, top + m))

        # Уменьшение до нужного размера (если нужно)
        if m > size:
            img = img.resize((size, size), Image.LANCZOS)

        # Сохраняем в JPEG с указанным качеством
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True, subsampling=0)
        return buf.getvalue()