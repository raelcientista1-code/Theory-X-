from fastapi import FastAPI, UploadFile, File, Form
from typing import List, Optional
from datetime import datetime
from PIL import Image
import io
import json

app = FastAPI(title="Adaptive Probability with Memory")

app = FastAPI(
    title="Adaptive Probability with Memory",
    description="Sistema adaptativo com entrada manual e visual",
    version="1.0.0"
)

# ===============================
# ESTADOS OFICIAIS DO SISTEMA
# ===============================
STATES = ["T", "D", "E"]


# ===============================
# MODELOS DE ENTRADA
# ===============================

class HistoryInput(BaseModel):
    manual_history: Optional[List[str]] = []


# ===============================
# ROTA RAIZ (FIX NOT FOUND)
# ===============================

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Adaptive Probability API está rodando",
        "endpoints": {
            "docs": "/docs",
            "calculate": "/calculate"
        }
    }


# ===============================
# TEORIA MATEMÁTICA (INALTERADA)
# ===============================

def adaptive_probability(history: List[str]):
    beta = 2.0
    epsilon = 1e-6

    t = len(history)
    if t == 0:
        return {s: round(1 / len(STATES), 4) for s in STATES}

    counts = {s: history.count(s) for s in STATES}
    freqs = {s: counts[s] / t for s in STATES}

    P0 = {s: 1 / len(STATES) for s in STATES}

    weights = {
        s: P0[s] * ((freqs[s] + epsilon) ** beta)
        for s in STATES
    }

    Z = sum(weights.values())

    return {
        s: round(weights[s] / Z, 4)
        for s in STATES
    }


def classify(p):
    if p >= 0.60:
        return "Probabilidade ALTA"
    elif p >= 0.35:
        return "Probabilidade MÉDIA"
    else:
        return "Probabilidade PEQUENA"


# ===============================
# MÓDULO VISUAL (GANCHO)
# ===============================

def image_to_sequence(image_bytes: bytes) -> List[str]:
    """
    Placeholder para visão computacional futura.
    """
    Image.open(io.BytesIO(image_bytes))
    return ["T", "D", "T", "E", "T"]


# ===============================
# ENDPOINT PRINCIPAL
# ===============================
@app.post("/calculate")
async def calculate(
    file: UploadFile = File(...),
    manual_history: Optional[str] = Form(None)
):
    if manual_history:
        history = json.loads(manual_history)
    else:
        history = []

    image_bytes = await file.read()

    return {
        "status": "ok",
        "filename": file.filename,
        "history_length": len(history),
        "message": "Imagem recebida com sucesso"
    }

