# Infraestructura de Data Centers "Green Ops"

Como parte central de nuestra misión en **NexusLeaf Technologies S.L.**, nuestra infraestructura está diseñada para operar con la huella de carbono más cercana a cero del mercado.

## Ubicaciones y Características de los Nodos

Nuestra plataforma **EcoNode** orquesta el tráfico hacia los siguientes centros de datos según la disponibilidad energética y la demanda de red:

### 1. Nodo Alfa (Islandia - Reikiavik)
*   **Fuente de Energía:** 100% Geotérmica e Hidroeléctrica.
*   **Refrigeración:** Free-cooling (Aire exterior).
*   **PUE (Power Usage Effectiveness):** 1.03 (Líder en la industria).
*   **Propósito Principal:** Entrenamiento de grandes modelos (como Verdant LLM) y procesos batch que no son sensibles a la latencia de red en Europa del Sur.

### 2. Nodo Beta (España - Huesca)
*   **Fuente de Energía:** 100% Solar y Eólica (Certificación de Garantía de Origen - GdO).
*   **Refrigeración:** Refrigeración líquida inmersiva de desarrollo propio.
*   **PUE:** 1.12
*   **Propósito Principal:** Inferencia rápida de Verdant LLM y consultas a Bamboo DB para clientes en la Península Ibérica, requiriendo latencia de < 20ms.

### 3. Nodo Gamma (Noruega - Oslo)
*   **Fuente de Energía:** 100% Hidroeléctrica.
*   **Refrigeración:** Free-cooling e intercambio con red de calefacción urbana.
*   **PUE:** 1.08
*   **Propósito Principal:** Respaldo (Backup) redundante y almacenamiento en frío (Cold Storage).

## Métrica de Éxito: "Carbon Routing"
Nuestro orquestador implementa algoritmos de *Carbon Routing*, que significa que redirige la computación en tiempo real hacia el centro de datos donde la intensidad de carbono de la red eléctrica es menor en ese momento específico. 
