# Parámetros Globales
FS = 12000  # Frecuencia de muestreo en Hz
J_MAX = 5   # Cantidad de sub-bandas
N_MUESTRAS = 120000  # 10 segundos de registro

# Multiplicadores de Falla Teóricos para Rodamiento SKF 6205
MULTIPLICADORES_SKF = {
    'BPFO': 3.585,  # Pista Externa
    'BPFI': 5.415,  # Pista Interna
    'BSF': 2.357    # Elemento Rodante (Bola)
}

TOLERANCIA_PEAK = 0.02  # 2% de desviación permitida