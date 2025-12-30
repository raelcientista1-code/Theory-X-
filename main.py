from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import datetime

app = FastAPI(title="Adaptive Probability API")

STATES = ["T", "D", "E"]

# ===============================
# MODELO DE ENTRADA (JSON)
# ===============================
class ManualInput(BaseModel):
    manual_history: str = ""

# ===============================
# FUNÇÃO DE PROBABILIDADE (SUA MATEMÁTICA — INTACTA)
# ===============================
def adaptive_probability(history: List[str]):
    beta = 2.0
    epsilon = 1e-6
    t = len(history)

    if t == 0:
        return {s: round(1/len(STATES), 4) for s in STATES}

    counts = {s: history.count(s) for s in STATES}
    freqs = {s: counts[s] / t for s in STATES}
    P0 = {s: 1 / len(STATES) for s in STATES}

    weights = {
        s: P0[s] * ((freqs[s] + epsilon) ** beta)
        for s in STATES
    }

    Z = sum(weights.values())

    return {s: round(weights[s] / Z, 4) for s in STATES}

def classify(p):
    if p >= 0.60:
        return "Probabilidade ALTA"
    elif p >= 0.35:
        return "Probabilidade MÉDIA"
    else:
        return "Probabilidade PEQUENA"

# ===============================
# ENDPOINT PRINCIPAL (JSON)
# ===============================
@app.post("/calculate")
async def calculate(data: ManualInput):
    history = [
        x.upper()
        for x in data.manual_history.replace(",", " ").split()
        if x.upper() in STATES
    ]

    probabilities = adaptive_probability(history)
    best_event = max(probabilities, key=probabilities.get)

    return {
        "timestamp": str(datetime.now()),
        "history": history,
        "total_observacoes": len(history),
        "repeticoes": {s: history.count(s) for s in STATES},
        "probabilidades": probabilities,
        "mais_provavel": best_event,
        "classificacao": classify(probabilities[best_event])
    }

# ===============================
# ENDPOINT RAIZ
# ===============================
@app.get("/")
def root():
    return {
        "status": "online",
        "message": "API funcionando corretamente",
        "como_usar": {
            "endpoint": "/calculate",
            "formato": "JSON",
            "exemplo": {
                "manual_history": "T D E T T D"
            }
        }
    }
