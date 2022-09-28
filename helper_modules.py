import base64
import requests

from flask import json
from Crypto.Cipher import AES

def translated_content(request, file_suf):
    """ Get translated content from json file
    :param request: the request parameter passed by the views
    :param file_suf: json file's (containing the translations) main suffix
    :return: translated content and the language the content is being translated to
    """
    tmp_lang = request.args.get("lang")
    lang = tmp_lang if tmp_lang in ["en", "it", "lt", "hr"] else "en"
    with open("tr/{}_{}.json".format(file_suf, lang), encoding='utf-8') as fp:
        loc_data = json.load(fp)
        return loc_data, lang

def decrypt(secret_key, cipher_text):
    """ Decrypt a secret key
    :param secret_key: the secret_key
    :param cipher_text: contains the iv (first 'block_size' bytes) and cipher_text (bytes left)
    """
    cipher_text = base64.b64decode(cipher_text.encode("utf-8"))
    iv = cipher_text[:AES.block_size]
    cipher_text = cipher_text[AES.block_size:]
    cipher = AES.new(secret_key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(cipher_text)
    return decrypted.decode("utf-8")


def country_location(country, api_key):
    """ Location of a country, retrieved from google api
    :param country: country_name
    :param api_key: the api_key
    :return: location coordinates (longitude, latitude) and zoom factor
    """
    resp = requests.get("https://maps.googleapis.com/maps/api/geocode/json",
                        params={"address": country,
                                "key": api_key
                                })

    results = resp.json().get("results")

    try:
        geom = results.pop().get("geometry")
        bounds = geom.get("bounds")
        northeast = bounds.get("northeast")
        southwest = bounds.get("southwest")
        location = geom.get("location")

        # If country area is larger than 165, zoom 5 else 6
        zoom = 5 if (northeast["lat"] - southwest["lat"]) * (northeast["lng"] - southwest["lng"]) > 165 else 6
    except Exception as e:
        return None, None

    return location, zoom



def lang_to_flag(lang):
    """ Return true flag code from lang code
    :param lang: the lang code
    :return: the flag code
    """
    lang_flag = {"en": "GB",
                 "lt": "LT",
                 "it": "IT",
                 "hr": "HR"
                 }
    return lang_flag.get(lang)

