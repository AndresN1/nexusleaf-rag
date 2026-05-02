# Política de Privacidad y Tratamiento de Datos

**Última actualización:** 15 de Mayo de 2023
**Empresa:** NexusLeaf Technologies S.L.

En NexusLeaf Technologies S.L. ("nosotros", "nuestro", "la Empresa"), estamos comprometidos con la protección de la privacidad y los datos de nuestros usuarios y clientes. Esta política describe cómo recopilamos, usamos y protegemos la información en nuestros servicios: EcoNode Serverless, Verdant LLM y Bamboo DB.

## 1. Privacidad por Diseño en Modelos de Lenguaje (Verdant LLM)
A diferencia de otros proveedores de IA, nuestro modelo **Verdant LLM** es un modelo de peso abierto y ejecución aislada. 
*   **No usamos los datos de sus prompts para reentrenar nuestros modelos fundacionales.**
*   Todos los procesos de inferencia se realizan en entornos *sandboxed* (aislados) en la memoria RAM y se destruyen inmediatamente tras completarse la solicitud.

## 2. Telemetría y EcoNode
Para optimizar el enrutamiento de cargas de trabajo y minimizar la huella de carbono, recopilamos telemetría de rendimiento y consumo:
*   Uso de CPU/GPU.
*   Latencia de red y geolocalización aproximada del origen de la petición (a nivel de ciudad, nunca IP completa).
Esta información está anonimizada y se utiliza exclusivamente para entrenar el algoritmo de *Carbon Routing*.

## 3. Almacenamiento en Bamboo DB
Los vectores almacenados en instancias gestionadas de Bamboo DB están encriptados en reposo (AES-256) y en tránsito (TLS 1.3). El cliente retiene la propiedad intelectual absoluta de todos los datos vectorizados.

## 4. Derechos RGPD
Cumplimos estrictamente con el Reglamento General de Protección de Datos (RGPD) europeo. Los usuarios tienen derecho a acceder, rectificar, suprimir u oponerse al tratamiento de sus datos personales contactando a nuestro DPO (Data Protection Officer) a través de `privacy@nexusleaf.es`.
