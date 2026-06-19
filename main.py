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
    archivos_mat = glob.glob('*.mat')
    
    if not archivos_mat:
        print("No se encontraron archivos .mat en el directorio actual.")
        return

    print(f"Se encontraron {len(archivos_mat)} archivos para analizar: {archivos_mat}\n")

    for ruta_archivo in archivos_mat:
        print("=" * 60)
        print(f"Iniciando análisis para el archivo: {ruta_archivo}...")
        
        try:
            senal_cruda = cargar_senal_mat(ruta_archivo)
        except Exception as e:
            print(f"Error al cargar el archivo {ruta_archivo}: {e}")
            continue
            
        N = len(senal_cruda)
        t = np.arange(N) / config.FS
        
        print("Calculando espectro de envolvente de la señal original...")
        env_cruda = calcular_envolvente(senal_cruda)
        fft_env_cruda = np.abs(np.fft.fft(env_cruda))
        frecs_cruda = np.fft.fftfreq(N, d=1.0/config.FS)
        
        idx_pos = frecs_cruda > 0
        frecs_plot_cruda = frecs_cruda[idx_pos]
        amp_plot_cruda = fft_env_cruda[idx_pos]
        
        num_bandas = 2 ** config.J_MAX
        print(f"Iniciando filtrado en {num_bandas} sub-bandas (J = {config.J_MAX})...")
        
        mejor_entropia = float('inf')
        senal_optima = None
        env_optimo = None
        j_optimo = -1
        
        frecuencias_teoricas = {
            'BPFI': config.FREQ_BPFI,
            'BPFO': config.FREQ_BPFO,
            'BSF': config.FREQ_BSF
        }

        for j in range(1, num_bandas + 1):
            # CORRECCIÓN: Filtramos iterativamente desde la señal cruda base
            # para no destruir la energía de las bandas superiores por el residuo
            senal_filtrada, _ = filtro_subbanda_iterativo(senal_cruda, config.FS, j, config.J_MAX)
            
            envolvente = calcular_envolvente(senal_filtrada)
            
            entropia = entropia_shannon_espectral(envolvente)
            
            if entropia < mejor_entropia:
                mejor_entropia = entropia
                senal_optima = senal_filtrada
                env_optimo = envolvente
                j_optimo = j
                
        print(f"\n¡Banda de resonancia encontrada!")
        print(f" -> Sub-banda óptima (j): {j_optimo}")
        print(f" -> Entropía mínima: {mejor_entropia:.4f}")
        
        print("\nBuscando peaks en el espectro del envolvente óptimo...")
        fft_env_optimo = np.abs(np.fft.fft(env_optimo))
        amp_plot_optima = fft_env_optimo[idx_pos]
        
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
                 print(f"El peak máximo evaluado ({frec_dom:.2f} Hz) no coincide con ninguna frecuencia teórica.")
        print("-" * 50)
                 
        print(f"\nGenerando dashboard de visualización para {ruta_archivo}...")
        graficar_resultados_tarea(
            t, senal_cruda, frecs_plot_cruda, amp_plot_cruda,
            senal_optima, frecs_plot_cruda, amp_plot_optima,
            frecuencias_teoricas
        )

if __name__ == '__main__':
    principal()