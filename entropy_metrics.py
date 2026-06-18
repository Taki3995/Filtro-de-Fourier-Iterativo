# entropy_metrics.py
import numpy as np

def entropia_shannon_espectral(envolvente):
    """
    Calcula la Entropía de Shannon sobre la amplitud espectral del envolvente,
    normalizada como una distribución de probabilidad marginal (P).
    """
    A = np.abs(np.fft.fft(envolvente))
    
    # Normalización: amplitud dividida por la sumatoria
    p = A / np.sum(A)
    
    # Se filtran valores cero para evitar el error matemático en log2(0)
    p = p[p > 0]
    
    entropia = -np.sum(p * np.log2(p))
    return entropia

def entropia_permutacion(senal, m=3, tau=1):
    """
    Calcula la Entropía de Permutación (PE). Evalúa el orden temporal subyacente
    de la serie, siendo altamente sensible a impactos mecánicos periódicos (anomalías).
    Reemplaza a Shannon espectral para obtener resultados óptimos.
    """
    N = len(senal)
    if N < m * tau:
        return 0.0
        
    # Construcción de la matriz de embedding dinámico
    n_patrones = N - (m - 1) * tau
    matriz_embedding = np.empty((n_patrones, m))
    for i in range(m):
        matriz_embedding[:, i] = senal[i * tau : i * tau + n_patrones]
        
    # Extracción de patrones ordinales (índices que ordenan los valores)
    patrones = np.argsort(matriz_embedding, axis=1)
    
    # Hash vectorial rápido para conteo de frecuencias de cada patrón
    hash_multiplicador = np.power(m, np.arange(m))
    hashes = np.sum(patrones * hash_multiplicador, axis=1)
    
    _, conteos = np.unique(hashes, return_counts=True)
    
    # Cálculo de probabilidad y entropía de los patrones
    p = conteos / n_patrones
    pe = -np.sum(p * np.log2(p))
    
    return pe