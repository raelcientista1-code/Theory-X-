from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional, List
from PIL import Image
import cv2
import numpy as np
import io
from datetime import datetime
import os

app = FastAPI(title="Adaptive Probability API")

STATES = ["T", "D", "E"]

# Mapeamento do estado para o arquivo de template
TEMPLATES = {
    "T": "T. Tigre Amarelo.png",
    "D": "D. Vermelho.png",
    "E": "E. Empate verde.png"
}

# ===============================
# Função de probabilidade
# ===============================
def adaptive_probability(history: List[str]):
    beta = 2.0
    epsilon = 1e-6
    t = len(history)
    if t == 0:
        return {s: round(1/len(STATES),4) for s in STATES}
    
    counts = {s: history.count(s) for s in STATES}
    freqs = {s: counts[s]/t for s in STATES}
    P0 = {s: 1/len(STATES) for s in STATES}
    weights = {s: P0[s]*((freqs[s]+epsilon)**beta) for s in STATES}
    Z = sum(weights.values())
    return {s: round(weights[s]/Z,4) for s in STATES}

def classify(p):
    if p>=0.60: return "Probabilidade ALTA"
    elif p>=0.35: return "Probabilidade MÉDIA"
    else: return "Probabilidade PEQUENA"

# ===============================
# Função de extração com template matching
# ===============================
def extract_sequence_from_image(image_bytes: bytes) -> List[str]:
    # Converte imagem para OpenCV
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    cv_image = np.array(image)
    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
    
    sequence = []
    for state in STATES:
        template_path = TEMPLATES[state]
        if not os.path.exists(template_path):
            continue
        template = cv2.imread(template_path)
        w, h = template.shape[1], template.shape[0]

        res = cv2.matchTemplate(cv_image, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8  # ajuste conforme necessário
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            sequence.append(state)

    return sequence

# ===============================

from fastapi import UploadFile, File, Form

@app.post("/calculate")
async def calculate(
    manual_history: str = Form(""),
    file: UploadFile = File(None)
):
    history = []

    # MANUAL
    if manual_history.strip():
        history = [
            x.upper()
            for x in manual_history.replace(",", " ").split()
            if x.upper() in ["T", "D", "E"]
        ]

    # IMAGEM
    if file:
        image_bytes = await file.read()
        extracted = extract_sequence_from_image(image_bytes)
        history.extend(extracted)

    probabilities = adaptive_probability(history)
    best_event = max(probabilities, key=probabilities.get)

    return {
        "history": history,
        "total": len(history),
        "probabilidades": probabilities,
        "mais_provavel": best_event,
        "classificacao": classify(probabilities[best_event])
    }
