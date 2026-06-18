# data_loader.py
import scipy.io
import numpy as np

def cargar_senal_mat(ruta_archivo):
    """
    Carga un archivo .mat de la CWRU y extrae como array 1D puro
    la señal de vibración del Drive End (acelerómetro base).
    """
    # Único uso de scipy autorizado: lectura del diccionario .mat
    mat_data = scipy.io.loadmat(ruta_archivo)
    
    # Búsqueda dinámica de la llave del acelerómetro Drive End
    # Ignora meta-datos internos de MATLAB (ej. '__header__')
    llave_de = None
    for key in mat_data.keys():
        if key.endswith('_DE_time'):
            llave_de = key
            break
            
    if llave_de is None:
        raise ValueError(f"No se encontró un vector válido '_DE_time' en {ruta_archivo}")
        
    # Extracción y aplanamiento a vector 1D de NumPy tipo float64
    senal_cruda = mat_data[llave_de].flatten().astype(np.float64)
    
    return senal_cruda