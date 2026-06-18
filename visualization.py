# visualization.py
import matplotlib.pyplot as plt

def graficar_resultados_tarea(t, senal_cruda, frecs_cruda, amp_cruda, 
                              senal_optima, frecs_optima, amp_optima, 
                              frecuencias_teoricas):
    """
    Genera una figura con 4 subgráficos (subplots) cumpliendo
    estrictamente con las instrucciones de visualización requeridas.
    """
    # Configuración del lienzo general
    fig, axs = plt.subplots(4, 1, figsize=(12, 16))
    fig.suptitle('Análisis de Anomalías: Filtrado Sub-banda Iterativo y Espectro de Envolvente', 
                 fontsize=16, fontweight='bold')

    # Diccionario de colores para los marcadores de frecuencias teóricas
    colores_marcadores = {'BPFI': 'red', 'BPFO': 'green', 'BSF': 'orange'}

    # 1. Serie cruda en el dominio del tiempo
    axs[0].plot(t, senal_cruda, color='gray', alpha=0.8)
    axs[0].set_title('1. Serie Temporal Cruda Original')
    axs[0].set_xlabel('Tiempo (s)')
    axs[0].set_ylabel('Amplitud')
    axs[0].grid(True, linestyle='--', alpha=0.6)

    # 2. Espectro envolvente de la señal cruda con marcadores teóricos
    axs[1].plot(frecs_cruda, amp_cruda, color='black', linewidth=1)
    axs[1].set_title('2. Espectro de Envolvente (Señal Cruda) - Sin frecuencias dominantes claras')
    axs[1].set_xlabel('Frecuencia (Hz)')
    axs[1].set_ylabel('Amplitud Espectral')
    axs[1].set_xlim(0, max(frecs_cruda) / 4) # Hacemos zoom a la zona de interés
    axs[1].grid(True, linestyle='--', alpha=0.6)
    
    # Inserción de líneas verticales para frecuencias teóricas de fallo en crudo
    for nombre, frec in frecuencias_teoricas.items():
        axs[1].axvline(x=frec, color=colores_marcadores[nombre], linestyle='--', 
                       linewidth=1.5, label=f'Teórica {nombre} ({frec:.2f} Hz)')
    axs[1].legend(loc='upper right')

    # 3. Serie temporal de la señal óptima filtrada (Sub-banda de menor entropía)
    axs[2].plot(t, senal_optima, color='blue', alpha=0.8)
    axs[2].set_title('3. Serie Temporal Óptima Filtrada (Sub-banda de menor Entropía)')
    axs[2].set_xlabel('Tiempo (s)')
    axs[2].set_ylabel('Amplitud')
    axs[2].grid(True, linestyle='--', alpha=0.6)

    # 4. Espectro envolvente de la señal óptima con marcadores teóricos
    axs[3].plot(frecs_optima, amp_optima, color='darkblue', linewidth=1.2)
    axs[3].set_title('4. Espectro de Envolvente (Señal Óptima) - Detección de Falla')
    axs[3].set_xlabel('Frecuencia (Hz)')
    axs[3].set_ylabel('Amplitud Espectral')
    axs[3].set_xlim(0, max(frecs_optima) / 4) # Zoom asimétrico igual que en crudo
    axs[3].grid(True, linestyle='--', alpha=0.6)
    
    # Inserción de líneas verticales en el espectro óptimo para confirmar cruce de peak
    for nombre, frec in frecuencias_teoricas.items():
        axs[3].axvline(x=frec, color=colores_marcadores[nombre], linestyle='--', 
                       linewidth=1.5, label=f'Teórica {nombre} ({frec:.2f} Hz)')
    axs[3].legend(loc='upper right')

    plt.tight_layout(rect=[0, 0.03, 1, 0.96]) # Ajuste para que el título principal no se superponga
    plt.show()