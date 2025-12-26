from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from PIL import Image
import io

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
    file: Optional[UploadFile] = File(None),
    data: Optional[HistoryInput] = None
):
    history: List[str] = []

    # 1️⃣ Entrada por imagem
    if file is not None:
        image_bytes = await file.read()
        history.extend(image_to_sequence(image_bytes))

    # 2️⃣ Entrada manual
    if data and data.manual_history:
        history.extend(data.manual_history)

    # 3️⃣ Cálculo
    probabilities = adaptive_probability(history)
    best_event = max(probabilities, key=probabilities.get)

    return {
        "timestamp": datetime.now().isoformat(),
        "total_observacoes": len(history),
        "repeticoes": {s: history.count(s) for s in STATES},
        "probabilidades": probabilities,
        "mais_provavel": best_event,
        "classificacao": classify(probabilities[best_event]),
        "historico_usado": history
    }
