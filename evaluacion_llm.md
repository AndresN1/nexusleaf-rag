# Batería de Pruebas: Validación del Modelo LLM (NexusLeaf)

Este documento contiene un conjunto de preguntas estratégicas basadas en el corpus de datos sintéticos de **NexusLeaf Technologies S.L.**. Úsalas como *prompts* de prueba (Golden Dataset) para evaluar si tu modelo ha interiorizado correctamente la información durante el proceso de *fine-tuning* o si el sistema RAG está recuperando los contextos adecuados.

---

## 1. Identidad Corporativa y Misión
**Pregunta:** ¿Cuál es el lema de NexusLeaf Technologies y cuál es su misión principal?
**Respuesta Esperada:** 
*   **Lema:** *"Conectando el mañana, respetando el hoy."*
*   **Misión:** Proveer infraestructura tecnológica de alto rendimiento y modelos de machine learning que minimicen la huella de carbono de las operaciones digitales empresariales.

## 2. Liderazgo y Recursos Humanos
**Pregunta:** ¿Quién ocupa el puesto de Head of Green Ops en la empresa y cuál es su responsabilidad principal?
**Respuesta Esperada:**
*   El puesto lo ocupa **Tariq Al-Fayed**.
*   Su responsabilidad principal es la auditoría de eficiencia energética en los centros de datos de la empresa.

## 3. Salud Financiera
**Pregunta:** ¿Cuánto capital levantó NexusLeaf en su ronda semilla de 2023 y quién lideró dicha inversión?
**Respuesta Esperada:**
*   Levantó **1,2 millones de euros** en marzo de 2023.
*   La ronda fue liderada por el fondo **Iberia Tech Ventures**.

## 4. Productos y Legal (Privacidad)
**Pregunta:** Si soy cliente de Verdant LLM, ¿mis prompts serán utilizados para entrenar versiones futuras del modelo?
**Respuesta Esperada:**
*   **No**. La política de privacidad establece claramente que no se usan los datos de los prompts para reentrenar modelos fundacionales. Además, los procesos de inferencia se realizan en entornos aislados (*sandboxed*) y se destruyen inmediatamente.

## 5. Logística e Infraestructura Verde
**Pregunta:** ¿Dónde se encuentra el "Nodo Alfa" de EcoNode, qué fuente de energía utiliza y cuál es su métrica PUE?
**Respuesta Esperada:**
*   **Ubicación:** Reikiavik, Islandia.
*   **Fuente de energía:** 100% Geotérmica e Hidroeléctrica.
*   **PUE:** 1.03.

## 6. Tecnología Core (Carbon Routing)
**Pregunta:** ¿En qué consiste exactamente el algoritmo de "Carbon Routing" que utiliza EcoNode?
**Respuesta Esperada:**
*   Es un sistema de orquestación que redirige las cargas de trabajo (la computación) en tiempo real hacia el centro de datos donde la intensidad de carbono de la red eléctrica es menor en ese momento específico.

## 7. Ventas y Soporte
**Pregunta:** ¿Qué niveles de soporte técnico ofrece NexusLeaf a sus clientes según su MRR?
**Respuesta Esperada:**
Ofrece tres niveles:
*   **Básico:** Para MRR menor a 1.000€.
*   **Prioritario:** Para MRR entre 1.000€ y 5.000€.
*   **Dedicado (SLA 99.99%):** Para clientes con un MRR superior a 5.000€.

## 8. Acuerdos Legales (NDA)
**Pregunta:** ¿Cuánto tiempo duran las obligaciones de confidencialidad para un empleado o contratista que firme un NDA con NexusLeaf una vez que deja la empresa?
**Respuesta Esperada:**
*   Las obligaciones subsisten por un período de **cinco (5) años** tras la terminación de la relación laboral o comercial.

## 9. Pruebas de Control de Alucinaciones (Respuestas Negativas)
Estas preguntas están diseñadas específicamente para evaluar si el modelo sabe reconocer sus límites y evitar inventar información (*alucinaciones*).

**Pregunta 9.1:** ¿Cuál fue la facturación exacta de NexusLeaf Technologies S.L. en el año 2021?
**Respuesta Esperada:** 
*   **"No dispongo de esa información"** (La empresa fue fundada en 2022, por lo que no existen registros del año 2021 en el corpus).

**Pregunta 9.2:** ¿Qué empresa competidora adquirió NexusLeaf Technologies a finales de 2023?
**Respuesta Esperada:**
*   **"No dispongo de esa información"** (El corpus menciona una ronda de inversión semilla en 2023, pero no detalla ninguna adquisición corporativa por parte de NexusLeaf).

**Pregunta 9.3:** ¿Cuáles son los detalles técnicos y la arquitectura de la versión de 14 billones de parámetros (14B) de Verdant LLM?
**Respuesta Esperada:**
*   **"No dispongo de esa información"** (El catálogo de productos especifica que Verdant LLM es un modelo de 7 mil millones de parámetros [7B]. No hay constancia de una versión 14B).

---
> **Tip para la evaluación:** Si el modelo responde correctamente a la mayoría de estas preguntas y rechaza cordialmente inventar respuestas a la sección 9, significará que ha asimilado correctamente tanto los archivos de texto/markdown como las lógicas extraídas de las bases de datos (CSVs), mitigando los riesgos de alucinación.
