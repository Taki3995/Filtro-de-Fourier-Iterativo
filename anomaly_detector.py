# anomaly_detector.py
import numpy as np

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
    Evalúa los picos de mayor amplitud comparándolos con las frecuencias teóricas.
    CORRECCIÓN: Revisa los Top 5 picos en lugar de solo el máximo absoluto para
    evitar que la frecuencia de rotación del motor (2X RPM) oculte la falla.
    """
    indices_picos = encontrar_picos_numpy(amplitudes)
    
    # Filtrar muy bajas frecuencias para ignorar ruido residual (< 10 Hz)
    indices_validos = [i for i in indices_picos if frecuencias[i] > 10.0]
    
    if not indices_validos:
        return False, None, 0.0, 0.0
        
    # Ordenar los índices de mayor a menor amplitud
    indices_ordenados = sorted(indices_validos, key=lambda i: amplitudes[i], reverse=True)
    
    # Seleccionar los Top 5 peaks de mayor energía
    top_indices = indices_ordenados[:5]
    
    # Comprobar la tolerancia (2%) contra cada uno de los mejores picos
    for idx in top_indices:
        frec_candidata = frecuencias[idx]
        amp_candidata = amplitudes[idx]
        
        for nombre_falla, frec_teorica in frecuencias_teoricas.items():
            limite_inferior = frec_teorica * (1.0 - tolerancia)
            limite_superior = frec_teorica * (1.0 + tolerancia)
            
            # Si ALGUNO de los peaks principales es una falla teórica, confirmar anomalía
            if limite_inferior <= frec_candidata <= limite_superior:
                return True, nombre_falla, frec_candidata, amp_candidata
                
    # Si no hubo match, retorna el peak #1 absoluto para registro visual
    idx_max_absoluto = top_indices[0]
    return False, None, frecuencias[idx_max_absoluto], amplitudes[idx_max_absoluto]