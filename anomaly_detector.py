import numpy as np
import config

def encontrar_picos_numpy(amplitudes):
    """
    Algoritmo nativo de NumPy para encontrar índices de máximos locales.
    """
    diff_izquierda = amplitudes[1:-1] - amplitudes[:-2]
    diff_derecha = amplitudes[1:-1] - amplitudes[2:]
    
    indices_picos = np.where((diff_izquierda > 0) & (diff_derecha > 0))[0] + 1
    return indices_picos

def evaluar_anomalia(frecuencias, amplitudes, frecuencias_teoricas, tolerancia):
    """
    Evalúa los picos de mayor amplitud comparándolos con las frecuencias teóricas puras.
    Utiliza un filtro dinámico inferior para evadir ruido estructural y de giro.
    """
    indices_picos = encontrar_picos_numpy(amplitudes)
    
    # Filtro dinámico: Ignorar frecuencias bajas basadas en la cinemática del eje
    limite_frecuencia = config.LOWER_LIMIT_MULTIPLIER * config.SHAFT_FREQ
    indices_validos = [i for i in indices_picos if frecuencias[i] > limite_frecuencia]
    
    if not indices_validos:
        return False, None, 0.0, 0.0
        
    # Ordenar los índices de mayor a menor amplitud
    indices_ordenados = sorted(indices_validos, key=lambda i: amplitudes[i], reverse=True)
    
    # Seleccionar solo los picos principales según configuración (Ej: Top 3)
    top_indices = indices_ordenados[:config.TOP_PEAKS_EVAL]
    
    # Comprobar la tolerancia (2%) contra las frecuencias teóricas para los peaks
    for idx in top_indices:
        frec_candidata = frecuencias[idx]
        amp_candidata = amplitudes[idx]
        
        for nombre_falla, frec_teorica in frecuencias_teoricas.items():
            limite_inferior = frec_teorica * (1.0 - tolerancia)
            limite_superior = frec_teorica * (1.0 + tolerancia)
            
            if limite_inferior <= frec_candidata <= limite_superior:
                return True, nombre_falla, frec_candidata, amp_candidata
                
    # Si no hubo match, retorna el peak #1 para registro visual
    idx_max_absoluto = top_indices[0]
    return False, None, frecuencias[idx_max_absoluto], amplitudes[idx_max_absoluto]