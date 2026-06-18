# main.py
import numpy as np
import glob
import config
from data_loader import cargar_senal_mat
from dsp_utils import filtro_subbanda_iterativo, calcular_envolvente
from entropy_metrics import entropia_permutacion, entropia_shannon_espectral
from anomaly_detector import evaluar_anomalia
from visualization import graficar_resultados_tarea

def principal():
    # 1. Buscar todos los archivos .mat en el directorio actual
    archivos_mat = glob.glob('*.mat')
    
    if not archivos_mat:
        print("No se encontraron archivos .mat en el directorio actual.")
        return

    print(f"Se encontraron {len(archivos_mat)} archivos para analizar: {archivos_mat}\n")

    # Iterar sobre cada archivo encontrado
    for ruta_archivo in archivos_mat:
        print("=" * 60)
        print(f"Iniciando análisis para el archivo: {ruta_archivo}...")
        
        try:
            senal_cruda = cargar_senal_mat(ruta_archivo)
        except Exception as e:
            print(f"Error al cargar el archivo {ruta_archivo}: {e}")
            continue  # Salta al siguiente archivo si hay un error
            
        N = len(senal_cruda)
        t = np.arange(N) / config.FS
        
        # 2. Análisis del espectro de la señal cruda (para el Gráfico 2)
        print("Calculando espectro de envolvente de la señal original...")
        env_cruda = calcular_envolvente(senal_cruda)
        fft_env_cruda = np.abs(np.fft.fft(env_cruda))
        frecs_cruda = np.fft.fftfreq(N, d=1.0/config.FS)
        
        # Filtramos solo el semieje de frecuencias positivas para los gráficos
        idx_pos = frecs_cruda > 0
        frecs_plot_cruda = frecs_cruda[idx_pos]
        amp_plot_cruda = fft_env_cruda[idx_pos]
        
        # 3. Descomposición Iterativa y Evaluación de Entropía
        num_bandas = 2 ** config.J_MAX
        print(f"Iniciando filtrado en {num_bandas} sub-bandas (J = {config.J_MAX})...")
        
        senal_actual = senal_cruda.copy()
        
        mejor_entropia = float('inf')
        senal_optima = None
        env_optimo = None
        j_optimo = -1
        
        # Diccionario de frecuencias de fallo importadas del config
        frecuencias_teoricas = {
            'BPFI': config.FREQ_BPFI,
            'BPFO': config.FREQ_BPFO,
            'BSF': config.FREQ_BSF
        }

        # Ciclo iterativo tal como indicó el profesor (j minúscula hasta 2^J)
        for j in range(1, num_bandas + 1):
            # Filtrado en frecuencia y extracción del residuo
            senal_filtrada, residuo = filtro_subbanda_iterativo(senal_actual, config.FS, j, config.J_MAX)
            senal_actual = residuo  # Descomposición en cascada de la señal remanente
            
            # Extracción de la amplitud de la señal analítica (Transformada de Hilbert)
            envolvente = calcular_envolvente(senal_filtrada)
            
            # Cálculo de Entropía
            # Usamos la de Permutación para mayor precisión en vibraciones impulsivas (Mejor Nota)
            # Puedes cambiarla por: entropia = entropia_shannon_espectral(envolvente)
            entropia = entropia_permutacion(senal_filtrada, m=3, tau=1)
            
            # Minimización de la entropía para encontrar la banda de resonancia
            if entropia < mejor_entropia:
                mejor_entropia = entropia
                senal_optima = senal_filtrada
                env_optimo = envolvente
                j_optimo = j
                
        print(f"\n¡Banda de resonancia encontrada!")
        print(f" -> Sub-banda óptima (j): {j_optimo}")
        print(f" -> Entropía mínima: {mejor_entropia:.4f}")
        
        # 4. Análisis del Espectro Óptimo y Detección del Fallo
        print("\nBuscando peaks en el espectro del envolvente óptimo...")
        fft_env_optimo = np.abs(np.fft.fft(env_optimo))
        amp_plot_optima = fft_env_optimo[idx_pos]
        
        # Verificación de anomalía según la tolerancia del 2%
        anomalia, falla, frec_dom, amp_dom = evaluar_anomalia(
            frecs_plot_cruda, amp_plot_optima, frecuencias_teoricas, config.TOLERANCIA_PEAK
        )
        
        print("-" * 50)
        if anomalia:
            print(f"RESULTADO: ¡Anomalía confirmada en {ruta_archivo}!")
            print(f" -> Componente dañada: {falla}")
            print(f" -> Frecuencia dominante detectada: {frec_dom:.2f} Hz")
            print(f" -> Frecuencia teórica esperada: {frecuencias_teoricas[falla]:.2f} Hz")
        else:
            print(f"RESULTADO: No se detectó ninguna anomalía en {ruta_archivo}.")
            if frec_dom is not None:
                 print(f"El peak máximo ({frec_dom:.2f} Hz) no coincide con ninguna frecuencia teórica.")
        print("-" * 50)
                 
        # 5. Visualización final
        print(f"\nGenerando dashboard de visualización para {ruta_archivo}...")
        # NOTA: Al ejecutar en lote, debes cerrar la ventana del gráfico de un archivo 
        # para que el programa continúe evaluando el siguiente.
        graficar_resultados_tarea(
            t, senal_cruda, frecs_plot_cruda, amp_plot_cruda,
            senal_optima, frecs_plot_cruda, amp_plot_optima,
            frecuencias_teoricas
        )

if __name__ == '__main__':
    principal()