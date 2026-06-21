"""rgb_control.py — RGB peripheral lighting control via OpenRGB SDK."""
from __future__ import annotations


def rgb_control(parameters=None, player=None, **kwargs):
    if parameters is None:
        parameters = {}
    action = parameters.get("action", "list")
    color = parameters.get("color", "rojo")
    brightness = parameters.get("brightness", 100)
    device = parameters.get("device", "")
    effect = parameters.get("effect", "")

    try:
        from openrgb import OpenRGBClient
        from openrgb.utils import RGBColor
    except ImportError:
        return "openrgb-python no instalado. Asegurate de tener OpenRGB corriendo con servidor SDK."

    try:
        client = OpenRGBClient()
        devices = client.devices

        if action == "list":
            if not devices:
                return "No se encontraron dispositivos RGB."
            return "Dispositivos RGB:\n" + "\n".join(f"  - {d.name} ({len(d.colors)} LEDs)" for d in devices)

        if action == "off":
            for d in devices:
                if not device or device.lower() in d.name.lower():
                    d.set_color(RGBColor(0, 0, 0))
            return "Luces RGB apagadas."

        if action == "set_color":
            color_map = {
                "rojo": (255, 0, 0), "verde": (0, 255, 0), "azul": (0, 0, 255),
                "blanco": (255, 255, 255), "negro": (0, 0, 0),
                "amarillo": (255, 255, 0), "cian": (0, 255, 255),
                "magenta": (255, 0, 255), "naranja": (255, 165, 0),
                "rosa": (255, 192, 203), "violeta": (238, 130, 238),
                "turquesa": (64, 224, 208), "gris": (128, 128, 128),
            }
            if color.startswith("#"):
                h = color.lstrip("#")
                rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
            else:
                rgb = color_map.get(color.lower(), (255, 255, 255))
            for d in devices:
                if not device or device.lower() in d.name.lower():
                    d.set_color(RGBColor(*rgb))
            return f"Color {color} aplicado."

        if action == "brightness":
            for d in devices:
                if not device or device.lower() in d.name.lower():
                    current = d.colors[0] if d.colors else RGBColor(255, 255, 255)
                    factor = brightness / 100
                    d.set_color(RGBColor(
                        int(current.red * factor),
                        int(current.green * factor),
                        int(current.blue * factor)
                    ))
            return f"Brillo ajustado a {brightness}%."

        if action == "rainbow":
            import colorsys
            for d in devices:
                if not device or device.lower() in d.name.lower():
                    colors = []
                    for i in range(len(d.colors)):
                        h = i / len(d.colors)
                        r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(h, 1.0, 1.0)]
                        colors.append(RGBColor(r, g, b))
                    d.set_color(colors)
            return "Efecto arcoíris aplicado."

        return f"RGB action '{action}' completado."
    except Exception as e:
        return f"Error RGB: {e}. Asegurate de que OpenRGB esté corriendo con servidor SDK activado."
