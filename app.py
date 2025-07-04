from flask import Flask, request, jsonify
import logging
from tuya_connector import TuyaOpenAPI, TUYA_LOGGER
from dialogflow import enviar_a_dialogflow
import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_ID = os.getenv("ACCESS_ID")
ACCESS_KEY = os.getenv("ACCESS_KEY")
API_ENDPOINT = os.getenv("API_ENDPOINT")
MQ_ENDPOINT = os.getenv("MQ_ENDPOINT")
DEVICE_ID = os.getenv("DEVICE_ID")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

app = Flask(__name__)

TUYA_LOGGER.setLevel(logging.DEBUG)
openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.connect()

COLOR_MAP = {
    "rojo": 0,
    "verde": 120,
    "azul": 240,
    "amarillo": 60,
    "rosado": 330,
    "violeta": 270
}

INTENSIDAD_MAP = {
    "baja": 20,
    "media": 500,
    "alta": 1000
}


@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.json
    params = body.get("queryResult", {}).get("parameters", {})

    accion = params.get("accion")
    color = params.get("color")
    intensidad = params.get("intensidad")
    dispositivo = params.get("dispositivo")

    commands = []

    if accion in ["encender"] and dispositivo:
        commands.append({"code": "switch_led", "value": True})

    if accion in ["apagar", "desactivar"] and dispositivo:
        commands.append({"code": "switch_led", "value": False})

    print (accion)

    if (accion in ["modificar"] and intensidad) and intensidad in INTENSIDAD_MAP:
        commands.append({"code": "bright_value_v2", "value": INTENSIDAD_MAP[intensidad]})



    if accion in ["modificar"] and color:
        if color == "blanco":
            # Modo blanco: intensidad + temperatura
            commands.append({"code": "bright_value_v2", "value": 800})  # brillo medio-alto
            commands.append({"code": "temp_value", "value": 500})       # blanco neutro
        elif color in COLOR_MAP:
            hue = COLOR_MAP[color]
            commands.append({
                "code": "colour_data_v2",
                "value": {
                    "h": hue,
                    "s": 1000,
                    "v": 1000
                }
            })


    if commands:
        
        payload = {"commands": commands}
        response = openapi.post("/v1.0/iot-03/devices/{}/commands".format(DEVICE_ID), payload)
        print("RESPUESTA TUYA:", response)
        success = response.get("success", False)
        result = response.get("result", False)
        return jsonify({
            "fulfillmentText": "He actualizado el dispositivo correctamente." if result else "No he podido actualizar el dispositivo."
        })

    return jsonify({"fulfillmentText": "No entendí qué hacer con el dispositivo."})


@app.route("/ordenar", methods=["POST"])
def ordenar():
    data = request.json
    texto = data.get("mensaje")

    respuesta_dialogflow = enviar_a_dialogflow(texto)

    return jsonify({"respuesta_dialogflow": respuesta_dialogflow})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
