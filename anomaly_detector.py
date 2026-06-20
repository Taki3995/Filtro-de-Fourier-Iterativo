import numpy as np
import config  # Importado para acceder a la velocidad del eje (SHAFT_FREQ)

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
    Evalúa los Top 20 picos de mayor amplitud comparándolos con las frecuencias teóricas puras.
    Ignora frecuencias por debajo de 65.0 Hz para evitar ruido estructural y de giro.
    """
    indices_picos = encontrar_picos_numpy(amplitudes)
    
    # Filtro estricto: Ignorar frecuencias bajas (incluyendo giro de motor 1X y 2X)
    indices_validos = [i for i in indices_picos if frecuencias[i] > 65.0]
    
    if not indices_validos:
        return False, None, 0.0, 0.0
        
    # Ordenar los índices de mayor a menor amplitud
    indices_ordenados = sorted(indices_validos, key=lambda i: amplitudes[i], reverse=True)
    
    # Seleccionar los Top 20 peaks de mayor energía (Asegura atrapar fallas tenues como BSF)
    top_indices = indices_ordenados[:20]
    
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