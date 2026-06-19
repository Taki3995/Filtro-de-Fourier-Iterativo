# anomaly_detector.py
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
    Evalúa los picos de mayor amplitud comparándolos con las frecuencias teóricas,
    incluyendo armónicos y bandas laterales producidas por el giro del eje.
    """
    indices_picos = encontrar_picos_numpy(amplitudes)
    
    # CORRECCIÓN: Filtro de corte en 65 Hz. Ignora completamente el 1X (29.5 Hz)
    # y el 2X (59.0 Hz) del giro del motor, obligando a buscar la resonancia.
    indices_validos = [i for i in indices_picos if frecuencias[i] > 65.0]
    
    if not indices_validos:
        return False, None, 0.0, 0.0
        
    # Ordenar los índices de mayor a menor amplitud
    indices_ordenados = sorted(indices_validos, key=lambda i: amplitudes[i], reverse=True)
    
    # Seleccionar los Top 5 peaks de mayor energía
    top_indices = indices_ordenados[:5]
    
    rpm_hz = config.SHAFT_FREQ  # 29.53 Hz
    
    # Comprobar la tolerancia (2%)
    for idx in top_indices:
        frec_candidata = frecuencias[idx]
        amp_candidata = amplitudes[idx]
        
        for nombre_falla, frec_teorica in frecuencias_teoricas.items():
            # CORRECCIÓN: Definir la "familia" de frecuencias para la falla
            # Incluye: Fundamental, Armónico 2X, y Bandas Laterales de 1er y 2do orden (+- RPM y +- 2*RPM)
            familia_frecuencias = [
                frec_teorica,
                frec_teorica * 2.0,
                frec_teorica - rpm_hz,
                frec_teorica + rpm_hz,
                frec_teorica - 2.0 * rpm_hz,  # Segunda banda lateral inferior (clave para 210.mat)
                frec_teorica + 2.0 * rpm_hz   # Segunda banda lateral superior
            ]
            
            for f_eval in familia_frecuencias:
                limite_inferior = f_eval * (1.0 - tolerancia)
                limite_superior = f_eval * (1.0 + tolerancia)
                
                # Si ALGUNO de los peaks coincide con la familia, confirmar anomalía
                if limite_inferior <= frec_candidata <= limite_superior:
                    return True, nombre_falla, frec_candidata, amp_candidata
                
    # Si no hubo match, retorna el peak #1 absoluto para registro visual
    idx_max_absoluto = top_indices[0]
    return False, None, frecuencias[idx_max_absoluto], amplitudes[idx_max_absoluto]