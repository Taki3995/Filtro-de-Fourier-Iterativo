# anomaly_detector.py
import numpy as np

def encontrar_picos_numpy(amplitudes):
    """
    Algoritmo nativo de NumPy para encontrar índices de máximos locales.
    Compara cada punto con sus vecinos adyacentes para prescindir de SciPy.
    """
    # Calculamos la diferencia entre puntos consecutivos
    diff_izquierda = amplitudes[1:-1] - amplitudes[:-2]
    diff_derecha = amplitudes[1:-1] - amplitudes[2:]
    
    # Un pico ocurre cuando es estrictamente mayor que ambos vecinos
    # Sumamos 1 para corregir el desfase del arreglo recortado
    indices_picos = np.where((diff_izquierda > 0) & (diff_derecha > 0))[0] + 1
    
    return indices_picos

def evaluar_anomalia(frecuencias, amplitudes, frecuencias_teoricas, tolerancia):
    """
    Extrae el pico de mayor amplitud del espectro de envolvente y lo cruza
    con las frecuencias teóricas permitiendo una tolerancia porcentual.
    """
    indices_picos = encontrar_picos_numpy(amplitudes)
    
    if len(indices_picos) == 0:
        return False, None, 0.0, 0.0

    # Filtramos la componente de corriente continua (DC) y bajas frecuencias (< 5 Hz)
    # que suelen dominar artificialmente el espectro del envolvente
    indices_validos = [i for i in indices_picos if frecuencias[i] > 5.0]
    
    if not indices_validos:
        return False, None, 0.0, 0.0
        
    # Encontrar el índice del pico con la amplitud máxima absoluta
    idx_max_amp = max(indices_validos, key=lambda i: amplitudes[i])
    frec_dominante = frecuencias[idx_max_amp]
    amp_dominante = amplitudes[idx_max_amp]
    
    # Comprobar la tolerancia (2%) contra cada frecuencia teórica
    anomalia_detectada = False
    falla_identificada = None
    
    for nombre_falla, frec_teorica in frecuencias_teoricas.items():
        limite_inferior = frec_teorica * (1.0 - tolerancia)
        limite_superior = frec_teorica * (1.0 + tolerancia)
        
        if limite_inferior <= frec_dominante <= limite_superior:
            anomalia_detectada = True
            falla_identificada = nombre_falla
            break
            
    return anomalia_detectada, falla_identificada, frec_dominante, amp_dominante