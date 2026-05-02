"""
Generador de Benchmark ampliado: 500 preguntas totales.
- Carga las 100 preguntas existentes de benchmark_rag.csv
- Añade 400 preguntas nuevas:
    * ID-based (EMP, CLI, GST): siempre usan el ID, nunca el nombre solo
    * Corpus/texto (Markdown): sobre productos, legal, finanzas
    * Consumo energético con timestamp exacto
    * Negativas/alucinación
- NO genera preguntas con nombres ambiguos sin ID
"""

import csv
import random
import os

random.seed(42)  # Reproducibilidad

# ─────────────────────────────────────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────────────────────────────────────

def load_csv(path):
    with open(path, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

empleados = load_csv('rrhh/empleados.csv')
clientes  = load_csv('clientes/base_clientes.csv')
gastos    = load_csv('finanzas/registro_gastos.csv')
consumos  = load_csv('logistica/registro_consumo_energetico.csv')

# ─────────────────────────────────────────────────────────────────
# CARGAR LAS 100 PREGUNTAS YA EXISTENTES
# ─────────────────────────────────────────────────────────────────

preguntas_existentes = load_csv('benchmark_rag.csv')
preguntas_ya_hechas = {p['pregunta'] for p in preguntas_existentes}

nuevas = []
id_counter = len(preguntas_existentes) + 1

def add_q(pregunta, tipo, respuesta):
    global id_counter
    if pregunta in preguntas_ya_hechas:
        return  # Evitar duplicados
    nuevas.append({
        'id': f"Q-{id_counter:03d}",
        'pregunta': pregunta,
        'tipo': tipo,
        'respuesta_esperada': respuesta
    })
    preguntas_ya_hechas.add(pregunta)
    id_counter += 1

# ─────────────────────────────────────────────────────────────────
# BLOQUE A: Empleados por ID (nunca por nombre solo)
# Generamos hasta 120 preguntas únicas basadas en EMP-XXXX
# ─────────────────────────────────────────────────────────────────

def preguntas_por_id_empleado(emp):
    return [
        (f"¿Cuál es el puesto exacto del empleado con ID {emp['ID']}?",
         "positiva", emp['Puesto']),
        (f"¿En qué departamento trabaja el empleado {emp['ID']}?",
         "positiva", emp['Departamento']),
        (f"¿Qué nivel de acceso tiene el empleado con ID {emp['ID']}?",
         "positiva", emp['Nivel_Acceso']),
        (f"¿Cuál es el salario anual del empleado {emp['ID']}?",
         "positiva", f"{emp['Salario_Anual_EUR']} EUR"),
        (f"¿En qué fecha fue contratado el empleado con ID {emp['ID']}?",
         "positiva", emp['Fecha_Contratacion']),
    ]

# Seleccionar empleados únicos que aporten variedad
ids_emp_usados = set()
intentos = 0
while len(nuevas) < 120 and intentos < 3000:
    intentos += 1
    emp = random.choice(empleados)
    plantillas = preguntas_por_id_empleado(emp)
    random.shuffle(plantillas)
    q, t, a = plantillas[0]
    add_q(q, t, a)

# ─────────────────────────────────────────────────────────────────
# BLOQUE B: Clientes por ID (CLI-XXXX)
# ─────────────────────────────────────────────────────────────────

def preguntas_por_id_cliente(cli):
    return [
        (f"¿Qué producto tiene contratado el cliente {cli['ID_Cliente']}?",
         "positiva", cli['Producto_Contratado']),
        (f"¿Qué nivel de soporte le corresponde al cliente {cli['ID_Cliente']}?",
         "positiva", cli['Nivel_Soporte']),
        (f"¿Cuál es el MRR mensual del cliente {cli['ID_Cliente']}?",
         "positiva", f"{cli['MRR_EUR']} EUR"),
        (f"¿Qué tipo de entidad es el cliente {cli['ID_Cliente']}?",
         "positiva", cli['Tipo']),
        (f"¿En qué fecha empezó la relación comercial con el cliente {cli['ID_Cliente']}?",
         "positiva", cli['Fecha_Inicio']),
    ]

objetivo_b = len(nuevas) + 100
intentos = 0
while len(nuevas) < objetivo_b and intentos < 3000:
    intentos += 1
    cli = random.choice(clientes)
    plantillas = preguntas_por_id_cliente(cli)
    random.shuffle(plantillas)
    q, t, a = plantillas[0]
    add_q(q, t, a)

# ─────────────────────────────────────────────────────────────────
# BLOQUE C: Gastos por ID (GST-XXX) — todos los registros
# ─────────────────────────────────────────────────────────────────

def preguntas_por_id_gasto(g):
    return [
        (f"¿Cuál fue el importe del gasto con ID {g['ID_Gasto']}?",
         "positiva", f"{g['Importe_EUR']} EUR"),
        (f"¿Qué categoría tiene el gasto {g['ID_Gasto']}?",
         "positiva", g['Categoria']),
        (f"¿A qué proveedor corresponde el gasto {g['ID_Gasto']}?",
         "positiva", g['Proveedor']),
        (f"¿Cuántos kg de CO₂ generó el gasto {g['ID_Gasto']}?",
         "positiva", f"{g['Impacto_Carbono_Kg']} kg"),
        (f"¿En qué fecha se registró el gasto con ID {g['ID_Gasto']}?",
         "positiva", g['Fecha']),
    ]

objetivo_c = len(nuevas) + 40
intentos = 0
while len(nuevas) < objetivo_c and intentos < 1000:
    intentos += 1
    gasto = random.choice(gastos)
    plantillas = preguntas_por_id_gasto(gasto)
    random.shuffle(plantillas)
    q, t, a = plantillas[0]
    add_q(q, t, a)

# ─────────────────────────────────────────────────────────────────
# BLOQUE D: Consumo energético (timestamp + nodo)
# ─────────────────────────────────────────────────────────────────

def preguntas_por_consumo(c):
    return [
        (f"El {c['Fecha_Hora']}, ¿qué porcentaje de GPU estaba usando el Nodo {c['Nodo']}?",
         "positiva", f"{c['Uso_GPU_Porc']}%"),
        (f"El {c['Fecha_Hora']}, ¿qué porcentaje de CPU usaba el Nodo {c['Nodo']}?",
         "positiva", f"{c['Uso_CPU_Porc']}%"),
        (f"El {c['Fecha_Hora']}, ¿cuántos kW consumía el Nodo {c['Nodo']}?",
         "positiva", f"{c['Consumo_kW']} kW"),
        (f"El {c['Fecha_Hora']}, ¿qué fuente de energía usaba el Nodo {c['Nodo']}?",
         "positiva", c['Origen_Energia']),
        (f"El {c['Fecha_Hora']}, ¿cuál era el PUE instantáneo del Nodo {c['Nodo']}?",
         "positiva", str(c['PUE_Instantaneo'])),
    ]

objetivo_d = len(nuevas) + 40
intentos = 0
while len(nuevas) < objetivo_d and intentos < 1000:
    intentos += 1
    con = random.choice(consumos)
    plantillas = preguntas_por_consumo(con)
    random.shuffle(plantillas)
    q, t, a = plantillas[0]
    add_q(q, t, a)

# ─────────────────────────────────────────────────────────────────
# BLOQUE E: Preguntas de corpus Markdown (texto estructurado)
# ─────────────────────────────────────────────────────────────────

corpus_qa = [
    # Identidad corporativa
    ("¿Cuál es el CIF de NexusLeaf Technologies?", "positiva", "B-98765432"),
    ("¿En qué planta se encuentra la sede de NexusLeaf?", "positiva", "Planta 4, Edificio B"),
    ("¿En qué ciudad está la sede central de NexusLeaf?", "positiva", "Valencia, España"),
    ("¿Cuáles son los valores corporativos de NexusLeaf? (Las 3 T)", "positiva",
     "Transparencia, Tenacidad y Trascendencia."),
    ("¿Qué significa 'Transparencia' en los valores de NexusLeaf?",
     "positiva", "Código abierto en herramientas fundamentales y métricas de consumo energético públicas en tiempo real."),
    ("¿Cuál es la visión de NexusLeaf para 2030?",
     "positiva", "Convertirse en el estándar europeo de computación verde para 2030."),
    ("¿Cuándo nació el proyecto NexusLeaf?", "positiva", "A finales de 2021 tras un hackathon de sostenibilidad tecnológica."),
    ("¿De qué hackathon surgió NexusLeaf?", "positiva", "Un hackathon de sostenibilidad tecnológica."),
    ("¿Qué herramienta original sirvió de núcleo para EcoNode?",
     "positiva", "Un script de orquestación de contenedores para optimizar el apagado de servidores inactivos."),
    ("¿Qué tono de comunicación usa NexusLeaf con clientes institucionales?", "positiva", "Uso de 'usted'."),
    ("¿Qué tono usa NexusLeaf en documentación técnica?", "positiva", "Uso de 'tú'."),
    # Productos
    ("¿Qué hace EcoNode Serverless?",
     "positiva", "Enruta dinámicamente las cargas de trabajo hacia centros de datos con energía renovable en momentos de baja demanda."),
    ("¿En cuánto se ha reducido el consumo de VRAM de Verdant LLM respecto al mercado?",
     "positiva", "En un 40%."),
    ("¿Para qué casos de uso está optimizado Verdant LLM?",
     "positiva", "Para auditorías legales y financieras."),
    ("¿Qué latencia ofrece Bamboo DB?", "positiva", "Latencia de milisegundos."),
    ("¿Qué tipo de aplicaciones usa Bamboo DB?", "positiva", "Aplicaciones de Generación Aumentada por Recuperación (RAG)."),
    # Infraestructura
    ("¿Qué fuente de energía usa el Nodo Alfa?", "positiva", "100% Geotérmica e Hidroeléctrica."),
    ("¿Qué tipo de refrigeración usa el Nodo Alfa?", "positiva", "Free-cooling (Aire exterior)."),
    ("¿Cuál es el propósito principal del Nodo Alfa?",
     "positiva", "Entrenamiento de grandes modelos y procesos batch no sensibles a la latencia."),
    ("¿Dónde está ubicado el Nodo Beta?", "positiva", "Huesca, España."),
    ("¿Cuál es el PUE del Nodo Beta?", "positiva", "1.12"),
    ("¿Qué fuente de energía usa el Nodo Beta?", "positiva", "100% Solar y Eólica."),
    ("¿Qué latencia máxima ofrece el Nodo Beta para la Península Ibérica?", "positiva", "< 20ms"),
    ("¿Dónde está ubicado el Nodo Gamma?", "positiva", "Oslo, Noruega."),
    ("¿Cuál es el PUE del Nodo Gamma?", "positiva", "1.08"),
    ("¿Qué fuente de energía usa el Nodo Gamma?", "positiva", "100% Hidroeléctrica."),
    ("¿Cuál es el propósito principal del Nodo Gamma?",
     "positiva", "Respaldo redundante y almacenamiento en frío (Cold Storage)."),
    ("¿Qué sistema de refrigeración usa el Nodo Gamma?",
     "positiva", "Free-cooling e intercambio con red de calefacción urbana."),
    # Legal / SLA
    ("¿Qué porcentaje de crédito recibe un cliente si el Uptime baja del 95%?",
     "positiva", "100% de la facturación mensual."),
    ("¿Qué porcentaje de crédito recibe si el Uptime está entre 99% y 99.95%?",
     "positiva", "10% de la facturación mensual."),
    ("¿Qué porcentaje de crédito recibe si el Uptime está entre 95% y 99%?",
     "positiva", "25% de la facturación mensual."),
    ("¿Cuántas horas de antelación avisa NexusLeaf de un mantenimiento programado?",
     "positiva", "Al menos 48 horas."),
    ("¿Qué porcentaje de ciclos de cómputo deben ser de energía renovable según el Green SLA?",
     "positiva", "Al menos el 95%."),
    ("¿Qué pasa si NexusLeaf no cumple el Green SLA mensual?",
     "positiva", "El cliente recibe créditos de carbono compensatorios."),
    ("¿Qué tipo de cifrado usa Bamboo DB en reposo?", "positiva", "AES-256."),
    ("¿Qué protocolo de cifrado usa Bamboo DB en tránsito?", "positiva", "TLS 1.3."),
    ("¿A quién pertenecen los datos vectorizados en Bamboo DB?",
     "positiva", "Al cliente, que retiene la propiedad intelectual absoluta."),
    ("¿Qué reglamento de protección de datos cumple NexusLeaf?",
     "positiva", "El RGPD (Reglamento General de Protección de Datos) europeo."),
    ("¿Cuál es el email del DPO de NexusLeaf?", "positiva", "privacy@nexusleaf.es"),
    ("¿Cuántos años dura la obligación de confidencialidad del NDA después de dejar la empresa?",
     "positiva", "5 años."),
    ("¿Quién debe autorizar la extracción de código según el NDA?",
     "positiva", "El CTO (Cozy Panda), de forma expresa y por escrito."),
    # Finanzas
    ("¿Cuándo se cerró el ejercicio fiscal del balance de 2023?",
     "positiva", "31 de Diciembre de 2023."),
    ("¿Cuáles fueron los ingresos operativos de NexusLeaf en 2023?",
     "positiva", "450.000 EUR por suscripciones a EcoNode y Bamboo DB."),
    ("¿Cuánto se gastó en gastos de personal en 2023?", "positiva", "580.000 EUR."),
    ("¿Cuánto se gastó en I+D en 2023?", "positiva", "150.000 EUR."),
    ("¿Cuál fue el beneficio neto de NexusLeaf en 2023?", "positiva", "605.000 EUR."),
    ("¿Cuándo se proyecta alcanzar el break-even operativo?",
     "positiva", "En el tercer trimestre de 2025."),
    ("¿Cuánto se invirtió en marketing y ventas en 2023?", "positiva", "65.000 EUR."),
]

for q, t, a in corpus_qa:
    add_q(q, t, a)

# ─────────────────────────────────────────────────────────────────
# BLOQUE F: Preguntas negativas adicionales (sin nombres ambiguos)
# ─────────────────────────────────────────────────────────────────

negativas_extra = [
    ("¿Cuál es el precio de la acción de NexusLeaf en bolsa?",
     "NexusLeaf no cotiza en bolsa, es una S.L. de capital privado."),
    ("¿Cuál es el número de teléfono de la sede de NexusLeaf?",
     "No hay número de teléfono publicado en la documentación."),
    ("¿Cuántos empleados tiene NexusLeaf en su oficina de Madrid?",
     "NexusLeaf no tiene oficina en Madrid, su sede es Valencia."),
    ("¿Qué puntuación NPS tiene NexusLeaf entre sus clientes?",
     "No hay información sobre encuestas de satisfacción o NPS en el corpus."),
    ("¿Cuál es la dirección de correo electrónico del CEO Elena Casanova?",
     "No se publica el email personal del CEO en la documentación."),
    ("¿Tiene NexusLeaf algún cliente en Asia?",
     "No hay datos de geolocalización de clientes más allá del ámbito español o europeo."),
    ("¿Cuánto cuesta la suscripción básica mensual de EcoNode?",
     "No se especifica un precio público de suscripción en la documentación."),
    ("¿Existe un plan gratuito (free tier) para Bamboo DB?",
     "No se menciona ningún plan gratuito en la documentación."),
    ("¿En qué cloud público está alojada la infraestructura principal de NexusLeaf?",
     "NexusLeaf tiene nodos propios (Alfa, Beta, Gamma). El único uso de cloud público mencionado fue un respaldo temporal en AWS (GST-003)."),
    ("¿Qué modelo de GPU usa el Nodo Gamma en Oslo?",
     "No se especifica el modelo de GPU del Nodo Gamma en la documentación."),
    ("¿Cuántos servidores físicos tiene el Nodo Beta en Huesca?",
     "No se detalla el número de servidores en la documentación de infraestructura."),
    ("¿Tiene NexusLeaf alguna patent registrada?",
     "No se menciona ninguna patente registrada en el corpus."),
    ("¿Hay un acuerdo de ERTE o ERE en NexusLeaf?",
     "No hay información sobre EREs o ERTEs en la documentación de RRHH."),
    ("¿Qué nota obtuvo NexusLeaf en la auditoría de ciberseguridad de 2023?",
     "No hay auditorías de ciberseguridad documentadas en el corpus."),
    ("¿Cuál es el número de registro mercantil de NexusLeaf?",
     "No se incluye el número de registro mercantil en la documentación."),
    ("¿Tiene NexusLeaf un programa de stock options para empleados?",
     "No se menciona ningún programa de stock options en el corpus."),
    ("¿Cuál fue el gasto en electricidad del Nodo Alfa durante 2023?",
     "No hay un desglose de gasto en electricidad por nodo en el registro de gastos."),
    ("¿Qué sistema de ticketing usa el equipo de Soporte Técnico?",
     "No se menciona el sistema de ticketing en la documentación."),
    ("¿Existe un acuerdo de partnership con Microsoft?",
     "No hay información sobre partnerships con Microsoft en la documentación."),
    ("¿Cuántos nodos de procesamiento tiene EcoNode en total?",
     "La documentación menciona tres nodos (Alfa, Beta, Gamma), pero no descarta que haya más no documentados."),
    ("¿Cuántos parámetros tiene el modelo Gemma que usa NexusLeaf internamente?",
     "NexusLeaf no usa Gemma internamente según el corpus. Su modelo propio es Verdant LLM de 7B."),
    ("¿Cuál es la capitalización de mercado de Iberia Tech Ventures?",
     "No hay información financiera sobre el fondo de inversión Iberia Tech Ventures en el corpus."),
    ("¿Qué nota tiene NexusLeaf en Glassdoor?",
     "No hay información sobre la valoración de empleados en plataformas como Glassdoor."),
    ("¿Cuál es la fecha de vencimiento del contrato con GreenDataCenter?",
     "No se especifican fechas de vencimiento de contratos con proveedores en el corpus."),
    ("¿Tiene NexusLeaf oficinas en Latinoamérica?",
     "No hay constancia de presencia en Latinoamérica en el corpus."),
    ("¿Cuánto se invirtió en formación de empleados en 2023?",
     "No se detalla una partida de formación de empleados en el balance de 2023."),
    ("¿Existe un Comité de Ética de IA en NexusLeaf?",
     "No se menciona ningún comité de ética en la documentación."),
    ("¿Qué plataforma de CI/CD usa el equipo de ingeniería?",
     "No se menciona la plataforma de CI/CD en el corpus."),
    ("¿Cuál es el presupuesto de marketing para 2024?",
     "No hay datos presupuestarios de 2024 en el corpus (solo el balance de 2023)."),
    ("¿Qué framework de machine learning usa el equipo de IA?",
     "No se especifica el framework de ML (PyTorch, TensorFlow, etc.) en la documentación."),
]

for q, a in negativas_extra:
    add_q(q, "negativa", a)

# ─────────────────────────────────────────────────────────────────
# COMBINAR, BARAJAR Y GUARDAR
# ─────────────────────────────────────────────────────────────────

# Re-numerar las preguntas existentes con los IDs originales
todas = preguntas_existentes + nuevas
random.shuffle(todas)

# Reasignar IDs correlativos
for i, p in enumerate(todas, start=1):
    p['id'] = f"Q-{i:03d}"

with open('benchmark_rag.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'pregunta', 'tipo', 'respuesta_esperada'])
    writer.writeheader()
    writer.writerows(todas)

total = len(todas)
positivas = sum(1 for p in todas if p['tipo'] == 'positiva')
negativas = sum(1 for p in todas if p['tipo'] == 'negativa')
print(f"[OK] Total preguntas: {total}")
print(f"  - Positivas: {positivas}")
print(f"  - Negativas: {negativas}")
print(f"Guardadas en 'benchmark_rag.csv'")
