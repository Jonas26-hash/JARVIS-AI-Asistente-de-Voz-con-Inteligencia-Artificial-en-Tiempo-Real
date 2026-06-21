"""social_media.py — Social media integration (Twitter/X, Instagram, LinkedIn)."""
from __future__ import annotations
import os, json
from pathlib import Path

_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def social_media(parameters=None, player=None, **kwargs):
    if parameters is None:
        parameters = {}
    platform = parameters.get("platform", "twitter")
    action = parameters.get("action", "")
    text = parameters.get("text", "")

    if platform == "setup":
        return ("Configuración de redes sociales:\n"
                "Twitter: crear app en developer.twitter.com, obtener API keys, guardarlas en config/twitter_keys.json\n"
                "Instagram: usar instagrapi con usuario/contraseña en config/instagram_creds.json\n"
                "LinkedIn: crear app en developer.linkedin.com")
    try:
        if platform == "twitter":
            from tweepy import Client, OAuth1UserHandler
            keys_file = _CONFIG_DIR / "twitter_keys.json"
            if not keys_file.exists():
                return "Twitter no configurado. Creá twitter_keys.json en config/ con api_key, api_secret, access_token, access_token_secret."
            keys = json.loads(keys_file.read_text())
            client = Client(
                consumer_key=keys["api_key"], consumer_secret=keys["api_secret"],
                access_token=keys["access_token"], access_token_secret=keys["access_token_secret"]
            )
            if action == "tweet":
                r = client.create_tweet(text=text)
                return f"Tweet publicado: {text[:50]}..."
            elif action == "timeline":
                tweets = client.get_home_timeline(max_results=5)
                return "Timeline:\n" + "\n".join(f"- {t.text[:100]}" for t in tweets.data or [])
            elif action == "search_tweets":
                query = parameters.get("query", "")
                tweets = client.search_recent_tweets(query=query, max_results=5)
                return f"Resultados para '{query}':\n" + "\n".join(f"- {t.text[:100]}" for t in tweets.data or [])
            return "Twitter action completado."

        elif platform == "instagram":
            from instagrapi import Client
            creds_file = _CONFIG_DIR / "instagram_creds.json"
            if not creds_file.exists():
                return "Instagram no configurado. Creá instagram_creds.json con username y password."
            creds = json.loads(creds_file.read_text())
            cl = Client()
            cl.login(creds["username"], creds["password"])
            if action in ("post", "upload_photo"):
                image_path = parameters.get("image_path", "")
                caption = parameters.get("caption", text)
                if os.path.isfile(image_path):
                    cl.photo_upload(image_path, caption)
                    return f"Foto publicada en Instagram."
                return "Falta image_path."
            elif action == "send_dm":
                receiver = parameters.get("username", "")
                user_id = cl.user_id_from_username(receiver)
                cl.direct_send(text, [user_id])
                return f"DM enviado a {receiver}."
            return "Instagram action completado."

        elif platform == "linkedin":
            return "LinkedIn requiere configuración de API en developer.linkedin.com. Usá browser_control para LinkedIn por ahora."

        return f"Social media platform '{platform}' action '{action}' completado."
    except ImportError as e:
        return f"Falta librería: {e}. Instalá con pip install tweepy instagrapi"
    except Exception as e:
        return f"Error en {platform}: {e}"
