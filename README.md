# cwru-bearing-anomaly-detection-dsp

Este proyecto implementa un sistema automatizado para el diagnóstico y detección de fallos en rodamientos utilizando técnicas avanzadas de Procesamiento Digital de Señales (DSP), sin depender de modelos de Machine Learning (caja negra). 

El algoritmo está diseñado para procesar señales de vibración y aislar transitorios de impacto mecánicos de baja energía que normalmente se encuentran enmascarados por el ruido electromagnético y rotacional del motor.

## Metodología

El núcleo matemático del proyecto se basa en los siguientes pasos algorítmicos implementados de manera nativa:

1. **Filtro de Sub-banda Iterativo de Fourier:** Descomposición de la señal original en `2^J` sub-bandas en el dominio de la frecuencia mediante el uso de ventanas rectangulares (FFT/IFFT).
2. **Análisis de Envolvente:** Construcción de la señal analítica utilizando la Transformada de Hilbert computada manualmente para extraer la envolvente de amplitud de las señales de alta frecuencia.
3. **Entropía Espectral de Shannon:** Optimización de la búsqueda de la banda de resonancia minimizando la entropía espectral. Se ignora la componente de corriente continua (DC) para asegurar que el algoritmo reaccione únicamente a la energía impulsiva de los fallos.
4. **Detección Automática de Anomalías:** Identificación de las frecuencias dominantes mediante un buscador de picos nativo. El algoritmo evalúa la "familia de frecuencias" de la cinemática del rodamiento (BPFI, BPFO, BSF), incluyendo armónicos y bandas laterales moduladas por la rotación del eje.

## Dataset Utilizado

El sistema está configurado y validado utilizando el benchmark estándar de la industria: **Case Western Reserve University (CWRU) Bearing Data Center**.

* **Condiciones de prueba por defecto:** Carga de 1 hp (velocidad del eje ~1772 RPM).
* **Frecuencia de muestreo:** 12,000 Hz.
* **Sensor analizado:** Acelerómetro del extremo de acoplamiento (Drive End - `_DE_time`).
* **Tipos de fallos detectables:** Pista interna (BPFI), Pista externa (BPFO) y Elemento rodante (BSF).

## Estructura del Proyecto

El código está modularizado para garantizar mantenibilidad y escalabilidad matemática:

* `config.py`: Definición de hiperparámetros (frecuencia de muestreo, niveles `J`, multiplicadores cinemáticos y RPM).
* `data_loader.py`: Extracción dinámica de vectores unidimensionales desde los diccionarios `.mat` (único módulo que utiliza SciPy).
* `dsp_utils.py`: Implementación pura en NumPy del enventanado frecuencial, filtros y la Transformada Rápida de Hilbert.
* `entropy_metrics.py`: Funciones de cálculo de Entropía de Shannon espectral (con supresión DC) y Entropía de Permutación.
* `anomaly_detector.py`: Algoritmo detector de máximos locales e identificador de bandas laterales con un margen de tolerancia del 2%.
* `visualization.py`: Construcción del dashboard de 4 subgráficos para contrastar la señal temporal y el espectro del envolvente.
* `main.py`: Orquestador principal que ejecuta el análisis en lote sobre todos los archivos `.mat` disponibles en el directorio.

## Requisitos

El proyecto restringe estrictamente el uso de librerías de alto nivel para el procesamiento de señales, apoyándose casi exclusivamente en la computación matricial base de Python.

* Python 3.8+
* numpy
* matplotlib
* scipy (exclusivo para `scipy.io.loadmat`)
* glob (librería estándar)

## Instrucciones de Uso

1. Clona el repositorio en tu entorno local.
2. Asegúrate de tener las dependencias instaladas: `pip install numpy matplotlib scipy`
3. Descarga los archivos `.mat` correspondientes al dataset CWRU (Ej: fallos a 1 hp en el Drive End) y colócalos en la raíz del proyecto junto a los scripts.
4. Ejecuta el orquestador principal desde la terminal:
   `python main.py`
5. El sistema procesará secuencialmente cada archivo `.mat` encontrado, mostrará los logs de entropía y picos detectados por consola, y desplegará un dashboard gráfico. Debes cerrar la ventana del gráfico actual para que el algoritmo procese el siguiente archivo.

## Resultados Visuales

El script genera un dashboard que consta de:
1. Serie Temporal Cruda Original.
2. Espectro de Envolvente Crudo (demostrando la ausencia de picos claros sin filtrar).
3. Serie Temporal Óptima Filtrada (Sub-banda de menor entropía).
4. Espectro de Envolvente Óptimo, donde el pico dominante se alinea perfectamente con la línea teórica del tipo de fallo (incluyendo tolerancia y modulación).
