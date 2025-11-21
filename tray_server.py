"""Tray launcher for the Tailscale Server Manager backend.

Keeps the FastAPI server running in the background while presenting a system
tray icon on Windows so the service stays visible and notifies you of issues.
"""

import threading
import webbrowser
from urllib.error import URLError
from urllib.request import urlopen

import uvicorn
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem
from win10toast import ToastNotifier

import server as server_module

HOST = "0.0.0.0"
PORT = 8765
HEALTH_CHECK_INTERVAL = 10
ICON_SIZE = 64

toaster = ToastNotifier()
stop_event = threading.Event()
server_instance = None


def notify(title: str, message: str) -> None:
    """Show a Windows toast without blocking the main thread."""
    try:
        toaster.show_toast(title, message, duration=6, threaded=True)
    except Exception:
        pass


def create_icon_image() -> Image.Image:
    """Create an in-memory icon so we do not ship additional assets."""
    image = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((4, 4, ICON_SIZE - 4, ICON_SIZE - 4), fill="#111827", outline="#b0c4ff")
    draw.ellipse((18, 18, ICON_SIZE - 18, ICON_SIZE - 18), fill="#6366f1")
    return image


def open_dashboard(icon: Icon, _item) -> None:
    """Open the dashboard in the user's browser."""
    webbrowser.open(f"http://localhost:{PORT}")


def stop_server() -> None:
    """Signal the UVicorn server instance to shut down."""
    global server_instance
    if server_instance is not None:
        server_instance.should_exit = True


def exit_action(icon: Icon, _item) -> None:
    """Tray menu handler that stops the server and removes the icon."""
    stop_event.set()
    stop_server()
    icon.stop()


def monitor_health() -> None:
    """Poll the /health endpoint and notify on repeated failures."""
    consecutive_failures = 0
    warning_displayed = False
    success_reported = False

    if stop_event.wait(timeout=2):
        return

    while not stop_event.is_set():
        try:
            with urlopen(f"http://localhost:{PORT}/health", timeout=5):
                pass
            consecutive_failures = 0
            if warning_displayed:
                notify("Tailscale Server Manager", "Health restored.")
                warning_displayed = False
            if not success_reported:
                notify("Tailscale Server Manager", f"Listening on http://localhost:{PORT}")
                success_reported = True
        except (URLError, Exception):
            consecutive_failures += 1
            if consecutive_failures >= 2 and not warning_displayed:
                notify(
                    "Tailscale Server Manager",
                    f"Cannot reach http://localhost:{PORT} - check the server logs.",
                )
                warning_displayed = True
        if stop_event.wait(timeout=HEALTH_CHECK_INTERVAL):
            break


def run_server_thread() -> None:
    """Run the FastAPI application in a background thread."""
    global server_instance
    config = uvicorn.Config(
        server_module.app,
        host=HOST,
        port=PORT,
        log_level="info",
        access_log=False,
        lifespan="on",
    )
    server_instance = uvicorn.Server(config)

    try:
        server_instance.run()
    except Exception as exc:
        notify("Tailscale Server Manager", f"Server stopped with error: {exc}")
    finally:
        stop_event.set()


def main() -> None:
    """Entry point for the tray launcher script."""
    server_thread = threading.Thread(target=run_server_thread, daemon=True)
    server_thread.start()
    health_thread = threading.Thread(target=monitor_health, daemon=True)
    health_thread.start()

    icon = Icon(
        "tailscale-server-manager",
        create_icon_image(),
        "Tailscale Server Manager",
        menu=Menu(
            MenuItem("Open Dashboard", open_dashboard),
            MenuItem("Exit", exit_action),
        ),
    )

    icon.run()

    stop_event.set()
    stop_server()
    server_thread.join(timeout=2)
    health_thread.join(timeout=2)


if __name__ == "__main__":
    main()
