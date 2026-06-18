# main.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import json

# Importar nuestros módulos
import config
import loader
import dsp

def generar_graficos(x_cruda, x_optima, fs, f_teorica, nombre_archivo, j_optima):
    """
    Genera la figura con los 4 sub-gráficos obligatorios solicitados en la rúbrica.
    """
    # Preparar vectores de tiempo
    N = len(x_cruda)
    t = np.arange(N) / fs
    
    # Calcular espectros de envolvente para graficar
    # 1. Señal cruda
    z_cruda = dsp.envolvente_hilbert_numpy(x_cruda)
    f_env_cruda, a_env_cruda = dsp.espectro_envolvente(z_cruda, fs)
    
    # 2. Señal óptima
    z_opt = dsp.envolvente_hilbert_numpy(x_optima)
    f_env_opt, a_env_opt = dsp.espectro_envolvente(z_opt, fs)
    
    # Armónicos a marcar (Frecuencia fundamental de falla y sus 3 primeros armónicos)
    armonicos = [f_teorica * i for i in range(1, 4)]
    
    # Crear la figura (4 subplots)
    fig, axs = plt.subplots(4, 1, figsize=(12, 16))
    fig.suptitle(f'Análisis de Rodamiento: {nombre_archivo}', fontsize=16)
    
    # Grafico 1: Serie temporal cruda
    axs[0].plot(t, x_cruda, color='gray')
    axs[0].set_title('1. Serie Temporal Cruda (Dominio del Tiempo)')
    axs[0].set_xlabel('Tiempo [s]')
    axs[0].set_ylabel('Amplitud')
    axs[0].grid(True)
    
    # Grafico 2: Amplitud Espectral de Envolvente (Señal Cruda)
    axs[1].plot(f_env_cruda, a_env_cruda, color='blue')
    for arm in armonicos:
        axs[1].axvline(x=arm, color='red', linestyle='--', alpha=0.7, label=f'{arm:.1f} Hz' if arm==armonicos[0] else "")
    axs[1].set_title('2. Espectro de Envolvente - Señal Cruda (Enmascaramiento)')
    axs[1].set_xlabel('Frecuencia [Hz]')
    axs[1].set_ylabel('Amplitud')
    axs[1].set_xlim(0, max(armonicos) + 100)
    axs[1].legend()
    axs[1].grid(True)
    
    # Grafico 3: Serie temporal óptima
    axs[2].plot(t, x_optima, color='green')
    axs[2].set_title(f'3. Serie Temporal Óptima (Banda j={j_optima})')
    axs[2].set_xlabel('Tiempo [s]')
    axs[2].set_ylabel('Amplitud')
    axs[2].grid(True)
    
    # Grafico 4: Amplitud Espectral de Envolvente (Señal Óptima)
    axs[3].plot(f_env_opt, a_env_opt, color='darkorange')
    for arm in armonicos:
        axs[3].axvline(x=arm, color='red', linestyle='--', alpha=0.7, label=f'{arm:.1f} Hz' if arm==armonicos[0] else "")
    axs[3].set_title('4. Espectro de Envolvente - Señal Óptima (Detección de Peak)')
    axs[3].set_xlabel('Frecuencia [Hz]')
    axs[3].set_ylabel('Amplitud')
    axs[3].set_xlim(0, max(armonicos) + 100)
    axs[3].legend()
    axs[3].grid(True)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    
    # Guardar figura
    nombre_imagen = f"resultados_{nombre_archivo.split('.')[0]}.png"
    plt.savefig(nombre_imagen)
    print(f"Gráficos guardados en: {nombre_imagen}")
    plt.close()

def main():
    archivos_mat = [f for f in os.listdir('.') if f.endswith('.mat')]
    if not archivos_mat:
        print("No se encontraron archivos .mat en el directorio.")
        return
        
    resultados_globales = {}

    for archivo in archivos_mat:
        print(f"\n{'='*50}\nProcesando: {archivo}\n{'='*50}")
        
        # 1. Cargar Datos
        x_cruda, rpm = loader.cargar_datos_mat(archivo)
        fs = config.FS
        
        # Fase 1: Sincronización
        freqs_teoricas = loader.fase1_sincronizacion_cinematica(rpm)
        
        # Fase 2: Filtro de Fourier
        sub_bandas = dsp.aplicar_filtro_iterativo(x_cruda, fs, config.J_MAX)
        
        # Fase 3 y 4: Entropía y Banda Óptima
        idx_optimo, f_opt, A_opt, E_min = dsp.buscar_banda_optima(sub_bandas, fs)
        j_optima = idx_optimo + 1
        senal_optima = sub_bandas[idx_optimo]
        
        # Fase 5: Peak y Correlación
        # Se filtra f_min=35.0 para ignorar el ruido de baja frecuencia (eje de rotación)
        f_peak, a_peak = dsp.encontrar_peak_dominante(f_opt, A_opt, f_min=35.0)
        
        anomalia_detectada = False
        falla_identificada = "Ninguna (Fuera del 2%)"
        f_teorica_referencia = None
        
        # Correlacionar con tolerancia del 2%
        for nombre, f_teo in freqs_teoricas.items():
            if nombre == 'f_r': continue
            
            limite_inf = f_teo * (1 - config.TOLERANCIA_PEAK)
            limite_sup = f_teo * (1 + config.TOLERANCIA_PEAK)
            
            if limite_inf <= f_peak <= limite_sup:
                anomalia_detectada = True
                falla_identificada = nombre
                f_teorica_referencia = f_teo
                break
                
        # Si no hubo coincidencia estricta, tomamos la teórica más cercana para la visualización
        if not anomalia_detectada:
            distancias = {nombre: abs(f_peak - f_teo) for nombre, f_teo in freqs_teoricas.items() if nombre != 'f_r'}
            falla_identificada = min(distancias, key=distancias.get)
            f_teorica_referencia = freqs_teoricas[falla_identificada]
            
        print(f"J mayúscula utilizada: {config.J_MAX}")
        print(f"Sub-banda óptima (j): {j_optima} (Entropía: {E_min:.4f})")
        print(f"Frecuencia Peak detectado: {f_peak:.2f} Hz")
        print(f"Falla referencial más cercana: {falla_identificada} a {f_teorica_referencia:.2f} Hz")
        print(f"¿Cumple tolerancia del 2%?: {'SÍ' if anomalia_detectada else 'NO'}")
        
        # Generar las visualizaciones
        generar_graficos(x_cruda, senal_optima, fs, f_teorica_referencia, archivo, j_optima)
        
        # Guardar en diccionario para exportar
        resultados_globales[archivo] = {
            "j_max_config": int(config.J_MAX),
            "j_optima_descubierta": int(j_optima),
            "entropia_minima": float(E_min),
            "frecuencia_peak_hz": float(f_peak),
            "anomalia_identificada": str(falla_identificada),
            "frecuencia_teorica_hz": float(f_teorica_referencia),
            "validacion_2_porciento": bool(anomalia_detectada)
        }
        
    # Exportar resultados a un archivo de configuración/salida
    with open("resultados_optimos.json", "w") as f:
        json.dump(resultados_globales, f, indent=4)
    print("\nArchivo 'resultados_optimos.json' generado con éxito.")

if __name__ == "__main__":
    main()