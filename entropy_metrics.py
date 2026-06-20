import numpy as np

def entropia_shannon_espectral(envolvente):
    """
    Calcula la Entropía de Shannon sobre la amplitud espectral.
    (Restaurada la función original que identificaba las bandas correctamente)
    """
    # 1. Calcular amplitud espectral de Fourier
    A = np.abs(np.fft.fft(envolvente))
    
    # 2. Solo tomar la mitad positiva del espectro (Nyquist)
    A = A[:len(A)//2]
    
    # 3. Anular la componente continua (0 Hz)
    A[0] = 0.0
    
    # 4. Normalizar para obtener la distribución de probabilidad
    suma_A = np.sum(A)
    if suma_A == 0:
        return float('inf')
        
    p = A / suma_A
    p = p[p > 0]  # Filtrar para evitar error matemático log2(0)
    
    # 5. Calcular entropía
    entropia = -np.sum(p * np.log2(p))
    return entropia

def entropia_permutacion(senal, m=3, tau=1):
    """
    Entropía de Permutación (Alternativa conservada).
    """
    N = len(senal)
    if N < m * tau:
        return 0.0
        
    n_patrones = N - (m - 1) * tau
    matriz_embedding = np.empty((n_patrones, m))
    for i in range(m):
        matriz_embedding[:, i] = senal[i * tau : i * tau + n_patrones]
        
    patrones = np.argsort(matriz_embedding, axis=1)
    
    hash_multiplicador = np.power(m, np.arange(m))
    hashes = np.sum(patrones * hash_multiplicador, axis=1)
    
    _, conteos = np.unique(hashes, return_counts=True)
    
    p = conteos / n_patrones
    pe = -np.sum(p * np.log2(p))
    
    return pe