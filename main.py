from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict
import requests
import time
import threading
import uvicorn

app = FastAPI(
    title="API de Preguntas y Respuestas",
    description="API que muestra preguntas y respuestas en formato JSON",
    version="2.0"
)

# ==================== DATOS ====================

preguntas_respuestas: Dict[str, str] = {
    "messi": "Quien es Leo Messi?",
    "balones": "Cuantos Balones de Oro tiene Messi?",
    "equipo": "En que equipo juega Messi actualmente?"
}

respuestas: Dict[str, str] = {
    "messi": "Lionel Andres Messi Cuccittini es un futbolista argentino considerado uno de los mejores jugadores de la historia.",
    "balones": "Hasta el año 2026, Lionel Messi tiene 8 Balones de Oro.",
    "equipo": "En 2026, Leo Messi juega en el Inter Miami de la MLS en Estados Unidos."
}

# ==================== ENDPOINT PRINCIPAL ====================

@app.get("/ask-batch")
async def ask_batch():
    """
    Devuelve preguntas y respuestas usando un FOR
    """

    try:
        data = {
            "questions": [
                {"key": "messi", "value": preguntas_respuestas["messi"]},
                {"key": "balones", "value": preguntas_respuestas["balones"]},
                {"key": "equipo", "value": preguntas_respuestas["equipo"]}
            ]
        }

        result = {}

        # FOR QUE RECORRE LAS PREGUNTAS
        for item in data["questions"]:

            key = item.get("key")
            pregunta = item.get("value")

            if not key or not pregunta:
                continue

            respuesta = respuestas.get(
                key,
                "Respuesta no encontrada"
            )

            result[key] = {
                "pregunta": pregunta,
                "respuesta": respuesta
            }

        return JSONResponse(
            content={
                "success": True,
                "results": result
            },
            media_type="application/json; charset=utf-8"
        )

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_type": type(e).__name__,
                "message": str(e)
            },
            media_type="application/json; charset=utf-8"
        )

# ==================== ENDPOINT RAIZ ====================

@app.get("/")
async def root():

    return JSONResponse(
        content={
            "message": "API funcionando correctamente"
        },
        media_type="application/json; charset=utf-8"
    )

# ==================== ENDPOINT INDIVIDUAL ====================

@app.get("/question/{key}")
async def get_question(key: str):

    if key not in preguntas_respuestas:

        raise HTTPException(
            status_code=404,
            detail="Pregunta no encontrada"
        )

    return JSONResponse(
        content={
            "success": True,
            "key": key,
            "pregunta": preguntas_respuestas[key],
            "respuesta": respuestas.get(key)
        },
        media_type="application/json; charset=utf-8"
    )

# ==================== PRUEBA AUTOMATICA CON REQUESTS ====================

def probar_con_requests():

    print("Esperando que el servidor inicie...")
    time.sleep(3)

    try:

        print("\nProbando API con requests...\n")

        response = requests.get(
            "http://127.0.0.1:8000/ask-batch",
            timeout=5
        )

        response.encoding = "utf-8"

        if response.status_code == 200:

            data = response.json()

            print("Respuesta exitosa!\n")

            for key, info in data["results"].items():

                print(f"{key.upper()}")
                print(f"Pregunta : {info['pregunta']}")
                print(f"Respuesta: {info['respuesta']}")
                print("-" * 70)

        else:

            print(f"Error HTTP: {response.status_code}")

    except requests.exceptions.Timeout:

        print("Error: Tiempo de espera agotado")

    except requests.exceptions.ConnectionError:

        print("Error: No se pudo conectar al servidor")

    except Exception as e:

        print(f"Error inesperado: {e}")

# ==================== MAIN ====================

if __name__ == "__main__":

    threading.Thread(
        target=probar_con_requests,
        daemon=True
    ).start()

    print("Iniciando servidor...\n")

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )
