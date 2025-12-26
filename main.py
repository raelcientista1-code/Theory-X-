from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional, List
from PIL import Image
import io
import json
from datetime import datetime

app = FastAPI(title="Adaptive Probability API")

STATES = ["T", "D", "E"]

# Função matemática
def adaptive_probability(history: List[str]):
    beta = 2.0
    epsilon = 1e-6
    t = len(history)
    if t == 0:
        return {s: round(1 / len(STATES), 4) for s in STATES}

    counts = {s: history.count(s) for s in STATES}
    freqs = {s: counts[s] / t for s in STATES}
    P0 = {s: 1 / len(STATES) for s in STATES}
    weights = {s: P0[s] * ((freqs[s] + epsilon) ** beta) for s in STATES}
    Z = sum(weights.values())
    return {s: round(weights[s] / Z, 4) for s in STATES}

def classify(p):
    if p >= 0.60:
        return "Probabilidade ALTA"
    elif p >= 0.35:
        return "Probabilidade MÉDIA"
    else:
        return "Probabilidade PEQUENA"

# Endpoint /calculate funcional
@app.post("/calculate")
async def calculate(
    file: UploadFile = File(...),
    manual_history: Optional[str] = Form(None)  # string JSON
):
    # 1️⃣ Histórico manual
    if manual_history:
        try:
            history = json.loads(manual_history)
        except json.JSONDecodeError:
            return {"error": "manual_history deve ser uma lista JSON válida"}
    else:
        history = []

    # 2️⃣ Processa imagem
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))

    # 3️⃣ Placeholder: extração da sequência da imagem
    # ⚠️ Aqui você pode integrar OCR depois
    extracted_sequence = ["T", "D", "E", "T", "D"]
    history.extend(extracted_sequence)

    # 4️⃣ Calcula probabilidades
    probabilities = adaptive_probability(history)
    best_event = max(probabilities, key=probabilities.get)

    return {
        "timestamp": str(datetime.now()),
        "filename": file.filename,
        "image_format": image.format,
        "image_size": image.size,
        "total_observacoes": len(history),
        "repeticoes": {s: history.count(s) for s in STATES},
        "probabilidades": probabilities,
        "mais_provavel": best_event,
        "classificacao": classify(probabilities[best_event])
        }
