# dsp_utils.py
import numpy as np

def filtro_subbanda_iterativo(senal, fs, j, J):
    """
    Aplica un filtro pasabanda ideal en el dominio de la frecuencia mediante una ventana rectangular.
    Retorna la señal filtrada para la j-ésima iteración y el residuo temporal.
    """
    N = len(senal)
    fft_senal = np.fft.fft(senal)
    freqs = np.fft.fftfreq(N, d=1.0/fs)
    
    nyquist = fs / 2.0
    ancho_banda = nyquist / (2**J)
    
    f_min = (j - 1) * ancho_banda
    f_max = j * ancho_banda
    
    # Construcción de ventana rectangular simétrica (frecuencias positivas y negativas)
    ventana = np.zeros(N)
    idx_banda = np.where((np.abs(freqs) >= f_min) & (np.abs(freqs) < f_max))[0]
    ventana[idx_banda] = 1.0
    
    # Filtrado y reconstrucción
    fft_filtrada = fft_senal * ventana
    senal_filtrada = np.real(np.fft.ifft(fft_filtrada))
    
    # Descomposición (la resta solicitada en las instrucciones)
    residuo = senal - senal_filtrada
    
    return senal_filtrada, residuo

def transformada_hilbert(senal):
    """
    Calcula la señal analítica usando la Transformada Rápida de Fourier (FFT),
    multiplicando por 2 las frecuencias positivas y anulando las negativas.
    """
    N = len(senal)
    X = np.fft.fft(senal)
    h = np.zeros(N)
    
    if N % 2 == 0:
        h[0] = 1
        h[N//2] = 1
        h[1:N//2] = 2
    else:
        h[0] = 1
        h[1:(N + 1)//2] = 2
        
    senal_analitica = np.fft.ifft(X * h)
    return senal_analitica

def calcular_envolvente(senal_filtrada):
    """
    Retorna la amplitud (valor absoluto) de la señal analítica (Envolvente).
    """
    return np.abs(transformada_hilbert(senal_filtrada))