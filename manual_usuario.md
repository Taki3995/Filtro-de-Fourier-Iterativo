# MANUAL_DE_USUARIO.txt

=========================================================
MANUAL DE USUARIO Y GUÍA DE ADAPTACIÓN DE DATASETS
Sistema de Detección de Anomalías DSP - CWRU
=========================================================

1. INTRODUCCIÓN AL SISTEMA
Este sistema está diseñado para procesar señales crudas de vibración y detectar automáticamente fallos mecánicos en rodamientos. Al ejecutar `main.py`, el sistema leerá automáticamente todos los archivos con extensión `.mat` en la misma carpeta, los procesará uno a uno, imprimirá un diagnóstico en la consola y generará un dashboard visual con los resultados.

2. CÓMO FUNCIONA EL ALGORITMO (FLUJO DE EJECUCIÓN)
- Lectura: Carga el archivo `.mat` y extrae la señal del sensor Drive End.
- Descomposición: Divide el espectro de frecuencias en sub-bandas usando un Filtro de Fourier.
- Selección: Calcula la Entropía de Shannon de cada sub-banda y selecciona la de menor valor (la que contiene la resonancia más limpia).
- Detección: Extrae el espectro de la señal óptima, filtra el ruido de baja frecuencia (< 65 Hz) y busca en los 20 picos de mayor amplitud si alguno coincide con las frecuencias de falla matemáticas (BPFI, BPFO, BSF) dentro de un margen de tolerancia estricto.

3. CONFIGURACIÓN POR DEFECTO
El sistema viene pre-configurado para el dataset estándar de la CWRU:
- Sensor: Drive End (Extremo del motor)
- Frecuencia de muestreo (FS): 12,000 Hz
- Carga: 1 HP (1772 RPM)

4. GUÍA DE ADAPTACIÓN PARA OTROS DATASETS (Ej: CWRU 48kHz)
Si deseas utilizar otros archivos de la misma base de datos (por ejemplo, los archivos grabados a 48,000 Hz o con diferentes cargas de motor), DEBES modificar los siguientes parámetros para evitar fallos matemáticos en la detección.

A) Modificaciones en `config.py`

   1. Frecuencia de Muestreo (FS):
      - ¿Por qué?: El algoritmo necesita saber cuántas muestras equivalen a 1 segundo para calcular correctamente la Transformada de Fourier.
      - Qué cambiar: Modifica `FS = 12000` al valor correspondiente de tu dataset (ej: `FS = 48000`).

   2. Niveles de Descomposición (J_MAX):
      - ¿Por qué?: Define la cantidad de sub-bandas (2^J). Al subir la frecuencia de muestreo, el ancho de banda total crece. Si no aumentas 'J', las bandas serán demasiado anchas y la entropía no podrá aislar el fallo.
      - Qué cambiar: Para 12k Hz usa `J_MAX = 5` (32 bandas). Para 48k Hz usa `J_MAX = 7` (128 bandas).

   3. Velocidad del Eje (RPM):
      - ¿Por qué?: Las frecuencias de fallo teóricas se calculan multiplicando la velocidad de giro por la cinemática del rodamiento. Si la carga del motor cambia, las RPM cambian, y si no lo ajustas, el algoritmo buscará la falla en la frecuencia equivocada.
      - Qué cambiar: Revisa la tabla de tu dataset y ajusta la variable `RPM`.
        * 0 HP = 1797 RPM
        * 1 HP = 1772 RPM
        * 2 HP = 1750 RPM
        * 3 HP = 1730 RPM

   4. Tolerancia de Detección (TOLERANCIA_PEAK):
      - ¿Por qué?: Es el margen de error permitido entre el pico detectado y la frecuencia matemática teórica.
      - Qué cambiar: Por defecto es `0.01` (1%). Si en otros datasets (como 48k) hay mayor fluctuación de velocidad en el motor, puedes relajar este parámetro a `0.02` (2%).

B) Modificaciones en `data_loader.py`

   1. Truncado de la Señal:
      - ¿Por qué?: El código original recorta la señal a 120,000 muestras para analizar exactamente 10 segundos de vibración a 12k Hz. Si cambias a 48k Hz, 120,000 muestras representarán solo 2.5 segundos, lo cual puede ser insuficiente para detectar impactos.
      - Qué cambiar: Busca la línea `senal_cruda = senal_cruda[:120000]`.
        - Cámbiala a `[:480000]` para mantener los mismos 10 segundos.
        - O elimínala/coméntala para procesar el archivo completo sin importar su duración.

NOTA FINAL:
Mientras no cambies el modelo físico del rodamiento (SKF 6205-2RS JEM), los multiplicadores cinemáticos (MULTIPLIER_BPFI, MULTIPLIER_BPFO, MULTIPLIER_BSF) no deben ser modificados.