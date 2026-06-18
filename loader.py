# loader.py
import numpy as np
import scipy.io as sio
from config import MULTIPLICADORES_SKF

def cargar_datos_mat(ruta_archivo):
    """
    Carga el archivo .mat y extrae la señal DE_time y el RPM.
    Maneja dinámicamente los nombres de las llaves que cambian según el archivo.
    """
    mat_data = sio.loadmat(ruta_archivo)
    
    # Buscar dinámicamente las llaves correctas ya que cambian (ej. X210_DE_time)
    llave_de = [key for key in mat_data.keys() if 'DE_time' in key][0]
    llave_rpm = [key for key in mat_data.keys() if 'RPM' in key]
    
    senal_de = mat_data[llave_de].flatten()
    
    # Algunos archivos .mat de CWRU tienen el RPM como llave, otros asumen ~1772-1797 para carga 1
    # Si la llave existe, la tomamos. Si no, usamos 1772 como valor por defecto para Carga 1.
    if llave_rpm:
        rpm = mat_data[llave_rpm[0]][0][0]
    else:
        rpm = 1772 
        
    return senal_de, rpm

def fase1_sincronizacion_cinematica(rpm):
    """
    Fase 1: Calcula la frecuencia fundamental y las frecuencias de falla teóricas.
    """
    f_r = rpm / 60.0
    
    frecuencias_teoricas = {
        'BPFO': MULTIPLICADORES_SKF['BPFO'] * f_r,
        'BPFI': MULTIPLICADORES_SKF['BPFI'] * f_r,
        'BSF': MULTIPLICADORES_SKF['BSF'] * f_r,
        'f_r': f_r
    }
    
    return frecuencias_teoricas

# Bloque de prueba rápida
if __name__ == "__main__":
    archivo_prueba = "210.mat"
    try:
        senal, rpm_val = cargar_datos_mat(archivo_prueba)
        frecuencias = fase1_sincronizacion_cinematica(rpm_val)
        
        print("=== RESULTADOS FASE 1 ===")
        print(f"Archivo: {archivo_prueba}")
        print(f"RPM extraído: {rpm_val}")
        print(f"Frecuencia Fundamental (fr): {frecuencias['f_r']:.2f} Hz")
        print(f"Frecuencia BPFO Teórica: {frecuencias['BPFO']:.2f} Hz")
        print(f"Frecuencia BPFI Teórica: {frecuencias['BPFI']:.2f} Hz")
        print(f"Frecuencia BSF Teórica: {frecuencias['BSF']:.2f} Hz")
        print("=========================")
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")