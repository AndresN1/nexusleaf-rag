import os
import csv
import random
from datetime import datetime, timedelta

# Crear directorios
folders = ['rrhh', 'finanzas', 'clientes', 'logistica', 'legal']
for f in folders:
    os.makedirs(f, exist_ok=True)

# ---------------------------------------------------------
# GENERAR EMPLEADOS (2000)
# ---------------------------------------------------------
nombres = ["Alejandro", "María", "David", "Laura", "Daniel", "Carmen", "Javier", "Ana", "Carlos", "Isabel", "Sergio", "Marta", "Jorge", "Lucía", "Pablo", "Elena", "José", "Paula", "Juan", "Sofía", "Marcos", "Tariq", "Cozy", "Héctor"]
apellidos = ["García", "Martínez", "López", "Sánchez", "Pérez", "Gómez", "Martín", "Jiménez", "Ruiz", "Hernández", "Díaz", "Moreno", "Álvarez", "Muñoz", "Romero", "Alonso", "Gutiérrez", "Navarro", "Torres", "Domínguez", "Casanova", "Llorens", "Panda", "Al-Fayed"]
departamentos = ["Ingeniería", "Operaciones Verdes", "Finanzas", "Ventas", "Marketing", "Recursos Humanos", "Legal", "Soporte Técnico"]
puestos_ing = ["Desarrollador Junior", "Desarrollador Senior", "Ingeniero de Machine Learning", "Arquitecto Cloud", "Ingeniero DevOps", "Data Scientist"]
puestos_op = ["Técnico de Data Center", "Ingeniero de Eficiencia Energética", "Especialista en Refrigeración", "Auditor Green Ops"]

empleados = []
# Equipo directivo (fijo)
empleados.append({
    "ID": "EMP-0001", "Nombre": "Elena", "Apellido": "Casanova", "Puesto": "CEO", "Departamento": "Dirección", 
    "Fecha_Contratacion": "2022-01-15", "Salario_Anual_EUR": 150000, "Nivel_Acceso": 5
})
empleados.append({
    "ID": "EMP-0002", "Nombre": "Cozy", "Apellido": "Panda", "Puesto": "CTO & Lead Architect", "Departamento": "Ingeniería", 
    "Fecha_Contratacion": "2022-01-15", "Salario_Anual_EUR": 140000, "Nivel_Acceso": 5
})
empleados.append({
    "ID": "EMP-0003", "Nombre": "Marcos", "Apellido": "Llorens", "Puesto": "CFO", "Departamento": "Finanzas", 
    "Fecha_Contratacion": "2022-02-01", "Salario_Anual_EUR": 130000, "Nivel_Acceso": 5
})
empleados.append({
    "ID": "EMP-0004", "Nombre": "Tariq", "Apellido": "Al-Fayed", "Puesto": "Head of Green Ops", "Departamento": "Operaciones Verdes", 
    "Fecha_Contratacion": "2022-03-10", "Salario_Anual_EUR": 125000, "Nivel_Acceso": 5
})

start_date = datetime(2022, 4, 1)
end_date = datetime(2024, 5, 1)

for i in range(5, 2001):
    dep = random.choices(departamentos, weights=[40, 15, 5, 15, 5, 5, 5, 10])[0]
    if dep == "Ingeniería":
        puesto = random.choice(puestos_ing)
    elif dep == "Operaciones Verdes":
        puesto = random.choice(puestos_op)
    else:
        puesto = f"Especialista en {dep}"
        
    salario = random.randint(25000, 80000)
    nivel = 1 if salario < 35000 else (2 if salario < 55000 else (3 if salario < 75000 else 4))
    
    delta_days = random.randint(0, (end_date - start_date).days)
    fecha = (start_date + timedelta(days=delta_days)).strftime("%Y-%m-%d")
    
    empleados.append({
        "ID": f"EMP-{i:04d}",
        "Nombre": random.choice(nombres),
        "Apellido": random.choice(apellidos),
        "Puesto": puesto,
        "Departamento": dep,
        "Fecha_Contratacion": fecha,
        "Salario_Anual_EUR": salario,
        "Nivel_Acceso": nivel
    })

with open("rrhh/empleados.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=empleados[0].keys())
    writer.writeheader()
    writer.writerows(empleados)


# ---------------------------------------------------------
# GENERAR CLIENTES (350)
# ---------------------------------------------------------
tipos_cliente = ["Particular", "Empresa", "Organización Gubernamental"]
sectores = ["Tecnología", "Salud", "Educación", "Finanzas", "Retail", "Administración Pública", "Manufactura"]
productos = ["EcoNode Serverless", "Verdant LLM", "Bamboo DB", "EcoNode + Bamboo DB", "Verdant LLM + Bamboo DB"]

empresas_nombres = ["Tech", "Soluciones", "Sistemas", "Innovación", "Global", "Data", "Cloud", "Verde"]
organizaciones = ["Ayuntamiento de", "Ministerio de", "Agencia Estatal de", "Universidad de", "Instituto Nacional de"]
ciudades = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Zaragoza", "Málaga", "Bilbao", "Murcia", "Alicante", "Córdoba"]

clientes = []
for i in range(1, 351):
    tipo = random.choices(tipos_cliente, weights=[10, 70, 20])[0]
    
    if tipo == "Particular":
        nombre = f"{random.choice(nombres)} {random.choice(apellidos)} {random.choice(apellidos)}"
        sector = "N/A"
    elif tipo == "Empresa":
        nombre = f"{random.choice(empresas_nombres)} {random.choice(empresas_nombres)} S.L."
        sector = random.choice(sectores[:-2]) # Evitar admin publica
    else:
        nombre = f"{random.choice(organizaciones)} {random.choice(ciudades)}"
        sector = "Administración Pública"
        
    producto = random.choice(productos)
    
    mrr = 0
    if tipo == "Particular":
        mrr = random.randint(50, 500)
    elif tipo == "Empresa":
        mrr = random.randint(500, 15000)
    else:
        mrr = random.randint(2000, 50000)
        
    soporte = "Básico" if mrr < 1000 else ("Prioritario" if mrr < 5000 else "Dedicado (SLA 99.99%)")
    
    delta_days = random.randint(0, (end_date - start_date).days)
    fecha_inicio = (start_date + timedelta(days=delta_days)).strftime("%Y-%m-%d")

    clientes.append({
        "ID_Cliente": f"CLI-{i:04d}",
        "Nombre_Entidad": nombre,
        "Tipo": tipo,
        "Sector": sector,
        "Producto_Contratado": producto,
        "Fecha_Inicio": fecha_inicio,
        "MRR_EUR": mrr,
        "Nivel_Soporte": soporte
    })

with open("clientes/base_clientes.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=clientes[0].keys())
    writer.writeheader()
    writer.writerows(clientes)

print("Datos de RRHH y Clientes generados con éxito.")
