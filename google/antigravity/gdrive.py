from __future__ import annotations
import urllib.parse


def preview_url(file_id: str) -> str:
    """Return a Google Drive preview URL that can be embedded in an iframe.

    Note: the file must be shared appropriately (anyone with link or viewer access).
    This does not download the file to the server — the client browser fetches it.
    """
    return f"https://drive.google.com/file/d/{urllib.parse.quote(file_id)}/preview"


def thumbnail_url(file_id: str, size: int = 800) -> str:
    """Return a best-effort thumbnail URL.

    Google Drive provides a thumbnail endpoint for files if the Drive API/permission allows it.
    For quick public thumb, the 'thumbnail' endpoint can be used; it may not work for restricted files.
    """
    # Use the thumbnail query parameter endpoint — note: for some files this URL is not available.
    return f"https://drive.google.com/thumbnail?id={urllib.parse.quote(file_id)}&sz={size}"


def iframe_embed_html(file_id: str, width: int = 800, height: int = 1000) -> str:
    """Return safe iframe HTML snippet for embedding Drive PDF preview in a static page.

    The caller is responsible for sanitizing file_id and ensuring share permissions.
    """
    src = preview_url(file_id)
    return f'<iframe src="{src}" width="{width}" height="{height}" allow="fullscreen"></iframe>'
