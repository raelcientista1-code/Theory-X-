"""
THEORY(X) — TEORIA DA PROBABILIDADE CONSERVATIVA ADAPTATIVA
=========================================================

Este módulo implementa formalmente a teoria proposta por Rael Cientista.

Ideia central:
- Todos os eventos possuem probabilidade inicial igual
- O sistema possui memória empírica
- Repetições reforçam probabilidades sem eliminar eventos
- A soma das probabilidades é sempre conservada
- O modelo é não-determinístico e adaptativo

Estados padrão do produto:
T = Tigre (Amarelo)
D = Dragão (Vermelho)
E = Empate (Verde)
"""

from typing import List, Dict
import math


class AdaptiveProbabilityTheory:
    """
    Implementação formal da teoria P(s | H).

    Operador fundamental:

        P(s | H) =
        ----------------------------------------
        P0(s) * ( f(s) + ε )^β
        ----------------------------------------
        Σ_u P0(u) * ( f(u) + ε )^β
    """

    def __init__(
        self,
        states: List[str],
        beta: float = 2.0,
        epsilon: float = 1e-6
    ):
        self.states = states
        self.beta = beta
        self.epsilon = epsilon

        # Axioma da igualdade inicial
        self.P0 = {s: 1 / len(states) for s in states}

    # ==================================================
    # HISTÓRICO E FREQUÊNCIA
    # ==================================================

    def count(self, history: List[str]) -> Dict[str, int]:
        """
        Contagem absoluta de repetições.
        """
        return {s: history.count(s) for s in self.states}

    def frequency(self, history: List[str]) -> Dict[str, float]:
        """
        Frequência empírica normalizada.
        """
        t = len(history)
        if t == 0:
            return {s: 0.0 for s in self.states}

        return {
            s: history.count(s) / t
            for s in self.states
        }

    # ==================================================
    # OPERADOR ADAPTATIVO CENTRAL
    # ==================================================

    def probability(self, history: List[str]) -> Dict[str, float]:
        """
        Calcula a distribuição de probabilidade adaptativa.
        """

        t = len(history)

        # Caso vazio: igualdade pura
        if t == 0:
            return {s: round(self.P0[s], 6) for s in self.states}

        freqs = self.frequency(history)

        weights = {
            s: self.P0[s] * ((freqs[s] + self.epsilon) ** self.beta)
            for s in self.states
        }

        Z = sum(weights.values())

        return {
            s: round(weights[s] / Z, 6)
            for s in self.states
        }

    # ==================================================
    # CLASSIFICAÇÃO QUALITATIVA
    # ==================================================

    def classify(self, p: float) -> str:
        """
        Classifica a intensidade da probabilidade.
        """
        if p >= 0.60:
            return "Probabilidade ALTA"
        elif p >= 0.35:
            return "Probabilidade MÉDIA"
        else:
            return "Probabilidade PEQUENA"

    # ==================================================
    # ANÁLISES AVANÇADAS (TEÓRICAS)
    # ==================================================

    def entropy(self, probabilities: Dict[str, float]) -> float:
        """
        Entropia de Shannon do sistema.
        Mede o grau de incerteza.
        """
        return -sum(
            p * math.log(p, 2)
            for p in probabilities.values()
            if p > 0
        )

    def most_likely(self, probabilities: Dict[str, float]) -> str:
        """
        Retorna o evento mais provável.
        """
        return max(probabilities, key=probabilities.get)

    # ==================================================
    # RELATÓRIO TEÓRICO
    # ==================================================

    def report(self, history: List[str]) -> Dict:
        """
        Relatório completo da teoria aplicada ao histórico.
        """

        probs = self.probability(history)
        best = self.most_likely(probs)

        return {
            "total_observacoes": len(history),
            "repeticoes": self.count(history),
            "frequencias": self.frequency(history),
            "probabilidades": probs,
            "mais_provavel": best,
            "classificacao": self.classify(probs[best]),
            "entropia": round(self.entropy(probs), 6),
        }