from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional, List
from PIL import Image
import io
from datetime import datetime

app = FastAPI(title="Adaptive Probability API")

# ===============================
# ESTADOS POSSÍVEIS
# ===============================
STATES = ["T", "D", "E"]  # T = Tigre, D = Dragão, E = Empate

# ===============================
# FUNÇÃO DE PROBABILIDADE
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
    if p >= 0.60:
        return "Probabilidade ALTA"
    elif p >= 0.35:
        return "Probabilidade MÉDIA"
    else:
        return "Probabilidade PEQUENA"

# ===============================
# ENDPOINT /calculate
# ===============================
@app.post("/calculate")
async def calculate(
    file: UploadFile = File(...),
    manual_history: Optional[str] = Form(None)  # string simples, não JSON
):
    # 1️⃣ Histórico manual
    history = []
    if manual_history:
        # Permite separar por espaço ou vírgula, sem precisar JSON
        history = [x.strip().upper() for x in manual_history.replace(",", " ").split()]
    
    # 2️⃣ Processa imagem
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))
    
    # 3️⃣ Placeholder de sequência extraída da imagem
    # Futuramente você substitui por OCR real
    extracted_sequence = ["T","D","E","T","D"]
    history.extend(extracted_sequence)
    
    # 4️⃣ Calcula probabilidades
    probabilities = adaptive_probability(history)
    best_event = max(probabilities, key=probabilities.get)
    
    # 5️⃣ Retorna JSON completo
    return {
        "timestamp": str(datetime.now()),
        "filename": file.filename,
        "image_format": image.format,
        "image_size": image.size,
        "total_observacoes": len(history),
        "repeticoes": {s: history.count(s) for s in STATES},
        "probabilidades": probabilities
