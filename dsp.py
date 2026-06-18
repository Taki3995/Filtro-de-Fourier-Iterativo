# dsp.py
import numpy as np

def aplicar_filtro_iterativo(x, fs, J):
    """
    Fase 2: Filtro de Fourier Pasa-bajo Iterativo.
    Descompone la señal en 2^J sub-bandas.
    """
    N = len(x)
    num_bandas = 2**J
    freqs = np.fft.fftfreq(N, 1/fs)
    
    x_actual = x.copy()
    sub_bandas = []
    
    for j in range(1, num_bandas + 1):
        # 1. Frecuencia de corte
        fc = j * (fs / 2) / num_bandas
        
        # 2. FFT de la señal actual
        X_f = np.fft.fft(x_actual)
        
        # 3. Ventana rectangular (simétrica para frecuencias pos/neg de la FFT)
        W = np.zeros(N)
        W[np.abs(freqs) <= fc] = 1
        
        # 4. Multiplicación e IFFT para obtener señal filtrada j-ésima
        X_filtrada = X_f * W
        x_j = np.real(np.fft.ifft(X_filtrada))
        
        sub_bandas.append(x_j)
        
        # 5. Restar a la señal original (actualizar)
        x_actual = x_actual - x_j
        
    return sub_bandas

def envolvente_hilbert_numpy(x):
    """
    Fase 3 (Parte 1): Transformada de Hilbert y Envolvente en Numpy puro.
    Crea la señal analítica eliminando frecuencias negativas y duplicando positivas.
    Retorna el valor absoluto z(t).
    """
    N = len(x)
    X_f = np.fft.fft(x)
    H = np.zeros(N, dtype=complex)
    
    # Construcción de señal analítica en frecuencia
    if N % 2 == 0:
        H[0] = X_f[0]
        H[N//2] = X_f[N//2]
        H[1:N//2] = 2 * X_f[1:N//2]
    else:
        H[0] = X_f[0]
        H[1:(N+1)//2] = 2 * X_f[1:(N+1)//2]
        
    z = np.fft.ifft(H)
    return np.abs(z)

def espectro_envolvente(z, fs):
    """
    Fase 3 (Parte 2): Amplitud Espectral del Envolvente a(t).
    Ignoramos la frecuencia 0 Hz (DC) ya que el promedio empuja el valor a niveles
    muy altos, arruinando el cálculo de la entropía.
    """
    N = len(z)
    A = np.abs(np.fft.fft(z))
    freqs = np.fft.fftfreq(N, 1/fs)
    
    idx_pos = freqs > 0  # Tomar solo f > 0 Hz
    return freqs[idx_pos], A[idx_pos]

def entropia_shannon(A):
    """
    Fase 3 (Parte 3): Calcula la Entropía de Shannon del espectro de amplitud.
    """
    # Normalizar para crear la distribución de probabilidad
    suma_A = np.sum(A)
    if suma_A == 0:
        return 0
    p = A / suma_A
    
    # Evitar log(0)
    p = p[p > 0]
    
    E = -np.sum(p * np.log(p))
    return E

def buscar_banda_optima(sub_bandas, fs):
    """
    Fase 4: Retorna el índice (j) de la banda con menor entropía, 
    sus frecuencias, su amplitud espectral y el valor de entropía.
    """
    entropias = []
    espectros = []
    
    for xj in sub_bandas:
        # Envolvente
        z = envolvente_hilbert_numpy(xj)
        # Espectro
        f, a = espectro_envolvente(z, fs)
        # Entropía
        E = entropia_shannon(a)
        
        entropias.append(E)
        espectros.append((f, a))
        
    idx_optimo = np.argmin(entropias)
    
    # Se retorna idx_optimo, las freqs óptimas, la amplitud óptima y la menor entropía
    return idx_optimo, espectros[idx_optimo][0], espectros[idx_optimo][1], entropias[idx_optimo]

def encontrar_peak_dominante(freqs, A, f_min=5.0):
    """
    Fase 5 (Parte 1): Detección de peak Numpy puro.
    Busca la frecuencia con mayor amplitud. f_min descarta ruido de muy baja frecuencia.
    """
    idx_validos = freqs >= f_min
    f_val = freqs[idx_validos]
    A_val = A[idx_validos]
    
    if len(A_val) == 0:
        return 0, 0
        
    idx_max = np.argmax(A_val)
    return f_val[idx_max], A_val[idx_max]

# Bloque de prueba rápida
if __name__ == "__main__":
    import loader
    import config
    
    archivo_prueba = "210.mat"
    print(f"Probando dsp.py con {archivo_prueba}...")
    senal, rpm_val = loader.cargar_datos_mat(archivo_prueba)
    
    # Probar Fase 2
    sub_bandas = aplicar_filtro_iterativo(senal, config.FS, config.J_MAX)
    print(f"Fase 2: {len(sub_bandas)} sub-bandas generadas correctamente (J={config.J_MAX}).")
    
    # Probar Fases 3 y 4
    idx_optimo, f_opt, A_opt, E_min = buscar_banda_optima(sub_bandas, config.FS)
    print(f"Fase 4: Banda óptima encontrada en índice {idx_optimo} (j={idx_optimo+1}) con entropía de {E_min:.4f}.")
    
    # Probar Fase 5 (Detección peak)
    f_peak, a_peak = encontrar_peak_dominante(f_opt, A_opt)
    print(f"Fase 5: Peak dominante detectado en {f_peak:.2f} Hz con amplitud {a_peak:.2f}.")