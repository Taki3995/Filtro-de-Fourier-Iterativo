# config.py

# Parámetros generales de la señal
FS = 12000  # Frecuencia de muestreo en Hz [cite: 139]
NYQUIST = FS / 2.0  # Límite del espectro de Nyquist (6000 Hz)

# Parámetros del filtro iterativo
J_MAX = 5  # Cantidad de niveles de sub-bandas (1 hasta 2^J)

# Parámetros mecánicos (Rodamiento Drive End - SKF 6205-2RS JEM) [cite: 164]
# Carga = 1 hp -> Velocidad del eje = 1772 RPM [cite: 1280]
RPM = 1772
SHAFT_FREQ = RPM / 60.0  # Frecuencia base del eje en Hz (~29.53 Hz)

# Multiplicadores de frecuencias teóricas de fallo [cite: 164]
MULTIPLIER_BPFI = 5.415  # Pista Interna (Inner Race)
MULTIPLIER_BPFO = 3.585  # Pista Externa (Outer Race)
MULTIPLIER_BSF = 2.357   # Elemento Rodante (Ball)

# Cálculo de frecuencias de fallo teóricas en Hz
FREQ_BPFI = MULTIPLIER_BPFI * SHAFT_FREQ
FREQ_BPFO = MULTIPLIER_BPFO * SHAFT_FREQ
FREQ_BSF = MULTIPLIER_BSF * SHAFT_FREQ

# Tolerancia del algoritmo de detección
TOLERANCIA_PEAK = 0.02  # 2% de desviación máxima aceptada