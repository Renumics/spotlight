"""Content security policy for the Spotlight frontend document."""

from urllib.parse import urlsplit

from renumics.spotlight.settings import Settings


def content_security_policy(nonce: str, origin: str, settings: Settings) -> str:
    """Allow the application resources without permitting arbitrary script execution."""
    url = urlsplit(origin)
    websocket_origin = f"{'wss' if url.scheme == 'https' else 'ws'}://{url.netloc}"
    connections = ["'self'", "blob:", websocket_origin]
    for allowed in settings.csp_connect_origins:
        connections.extend(
            [allowed, allowed.replace("https://", "wss://").replace("http://", "ws://")]
        )
    directives = {
        "default-src": ["'self'"],
        "script-src": ["'self'", f"'nonce-{nonce}'", *settings.csp_script_origins],
        "script-src-attr": ["'none'"],
        # React style attributes and styled-components require inline styles.
        "style-src": ["'self'", "'unsafe-inline'"],
        "img-src": ["'self'", "data:", "blob:", "https:", "http:"],
        "media-src": ["'self'", "data:", "blob:"],
        "font-src": ["'self'", "data:"],
        "connect-src": connections,
        "worker-src": ["'self'", "blob:"],
        "frame-src": ["'self'", "blob:"],
        "object-src": ["'none'"],
        "base-uri": ["'none'"],
        "form-action": ["'none'"],
    }
    # frame-ancestors is intentionally omitted to preserve iframe embedding.
    return "; ".join(
        f"{directive} {' '.join(dict.fromkeys(sources))}"
        for directive, sources in directives.items()
    )
