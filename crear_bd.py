import os
import pickle
import pandas as pd
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# 1. Configuración de carpetas
DIRECTORIO_DATOS = "./data" # Asegúrate de que esta es tu carpeta
DIRECTORIO_BD = "./chroma_db"

documentos = []

# 2. Funciones de carga especializada
def procesar_markdown(ruta):
    try:
        loader = TextLoader(ruta, encoding="utf-8")
        docs = loader.load()
        # Los Markdowns sí los cortamos por caracteres
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        return text_splitter.split_documents(docs)
    except Exception as e:
        print(f"Advertencia: Error en markdown {ruta}. Error: {e}")
        return []

def procesar_csv(ruta):
    docs = []
    try:
        df = pd.read_csv(ruta, encoding="utf-8")
        
        # El truco: Convertimos cada fila en un "Documento" con contexto completo
        for index, row in df.iterrows():
            # Creamos una cadena de texto que describe la fila entera
            contenido_fila = f"Datos del archivo {os.path.basename(ruta)}, fila {index + 1}:\n"
            for col in df.columns:
                contenido_fila += f"- {col}: {row[col]}\n"
            
            # Guardamos la metadata para saber de dónde salió
            doc = Document(
                page_content=contenido_fila,
                metadata={"source": ruta, "fila": index + 1}
            )
            docs.append(doc)
    except Exception as e:
         print(f"Advertencia: Error en CSV {ruta}. Error: {e}")
    return docs

# 3. Leer todos los archivos y procesar
print("Buscando archivos y procesando inteligentemente...")
fragmentos = []
for raiz, _, archivos in os.walk(DIRECTORIO_DATOS):
    for archivo in archivos:
        ruta_completa = os.path.join(raiz, archivo)
        
        if archivo.endswith(".md") or archivo.endswith(".txt"):
            fragmentos.extend(procesar_markdown(ruta_completa))
        elif archivo.endswith(".csv"):
            fragmentos.extend(procesar_csv(ruta_completa))

print(f"Se han creado {len(fragmentos)} fragmentos (chunks/filas) para indexar.")

if len(fragmentos) == 0:
    print("¡Error! No se han encontrado textos. Revisa la ruta de la carpeta.")
    exit()

# 4. Cargar modelo de embeddings (¡Acelerado por GPU!)
print("Cargando modelo de embeddings en la GPU...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    model_kwargs={'device': 'cuda'} # Movido a la gráfica para salvar tu CPU
)

# 5. Borrar la BD anterior (Opcional pero recomendado al cambiar la estructura)
import shutil
if os.path.exists(DIRECTORIO_BD):
    print("Borrando base de datos antigua...")
    shutil.rmtree(DIRECTORIO_BD)

# 6. Crear la base de datos vectorial
print("Creando base de datos vectorial (ChromaDB)...")
vectorstore = Chroma.from_documents(
    documents=fragmentos,
    embedding=embeddings,
    persist_directory=DIRECTORIO_BD
)

print("¡Base de datos vectorial creada con éxito!")

# 7. Guardar fragmentos en disco para el índice BM25
# (el índice BM25 opera sobre texto plano, no necesita embeddings)
print("Guardando fragmentos para el índice BM25...")
with open("./fragmentos_bm25.pkl", "wb") as f:
    pickle.dump(fragmentos, f)

print(f"✓ Guardados {len(fragmentos)} fragmentos en 'fragmentos_bm25.pkl'")
print("\n¡Todo listo! Puedes ejecutar chatbot.py o benchmark.py.")
