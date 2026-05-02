import re
import os
import glob
import pickle
import pandas as pd
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


# ─────────────────────────────────────────────────────────────────
# CONSTANTES: Patrones de IDs estructurados de NexusLeaf
# ─────────────────────────────────────────────────────────────────

# Cada entrada: (prefijo, columna_id_en_csv)
# El glob encuentra el CSV correcto automáticamente en cualquier subcarpeta de data/
PATRON_IDS = re.compile(r'\b(GST|CLI|EMP)-(\d{3,4})\b', re.IGNORECASE)

PREFIJO_A_COLUMNA = {
    "GST": "ID_Gasto",
    "CLI": "ID_Cliente",
    "EMP": "ID",
}


# ─────────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────────

def _encontrar_csvs(directorio_datos="./data"):
    """Devuelve un diccionario {ruta_csv: dataframe} para todos los CSV del directorio."""
    csvs = {}
    for ruta in glob.glob(os.path.join(directorio_datos, "**", "*.csv"), recursive=True):
        try:
            csvs[ruta] = pd.read_csv(ruta, encoding="utf-8", dtype=str)
        except Exception as e:
            print(f"  [Aviso] No se pudo leer {ruta}: {e}")
    return csvs


def _buscar_id_en_csv(id_buscado, prefijo, csvs):
    """
    Busca un ID exacto en todos los DataFrames cargados.
    Devuelve un Document con la fila completa o None si no se encuentra.
    """
    columna = PREFIJO_A_COLUMNA.get(prefijo.upper())
    if not columna:
        return None

    for ruta, df in csvs.items():
        if columna not in df.columns:
            continue

        # Comparación normalizada a mayúsculas para evitar fallos de capitalización
        mascara = df[columna].str.upper() == id_buscado.upper()
        fila = df[mascara]

        if not fila.empty:
            # Convertir la fila a texto descriptivo igual que en crear_bd.py
            row = fila.iloc[0]
            nombre_archivo = os.path.basename(ruta)
            contenido = f"Datos del archivo {nombre_archivo}, búsqueda directa por ID:\n"
            for col in df.columns:
                contenido += f"- {col}: {row[col]}\n"

            return Document(
                page_content=contenido,
                metadata={"source": ruta, "busqueda": "id_directo", "id": id_buscado}
            )

    return None  # ID no encontrado en ningún CSV


# ─────────────────────────────────────────────────────────────────
# CLASE PRINCIPAL: SmartHybridRetriever
# ─────────────────────────────────────────────────────────────────

class SmartHybridRetriever:
    """
    Retriever inteligente con tres niveles de búsqueda:

    1. ID Directo (GST-XXX, CLI-XXXX, EMP-XXXX):
       → Búsqueda exacta en CSV con pandas. 100% preciso, ~0ms extra.

    2. BM25 (Léxico):
       → Tokenización y ranking por frecuencia de palabras. Bueno para
          nombres propios, términos técnicos específicos.

    3. Vectorial Semántico (ChromaDB):
       → Embeddings. Bueno para preguntas por significado o paráfrasis.

    Niveles 2 y 3 se fusionan con Reciprocal Rank Fusion (RRF).
    """

    def __init__(
        self,
        bm25_retriever,
        vector_retriever,
        csvs_cargados,
        k=3,
        peso_bm25=0.5,
        peso_vector=0.5
    ):
        self.bm25_retriever = bm25_retriever
        self.vector_retriever = vector_retriever
        self.csvs = csvs_cargados
        self.k = k
        self.peso_bm25 = peso_bm25
        self.peso_vector = peso_vector

    def _rrf(self, listas_docs, pesos, k_rrf=60):
        """Reciprocal Rank Fusion: combina y reordena múltiples listas de resultados."""
        scores = {}
        for lista, peso in zip(listas_docs, pesos):
            for rank, doc in enumerate(lista):
                clave = doc.page_content
                if clave not in scores:
                    scores[clave] = {"doc": doc, "score": 0.0}
                scores[clave]["score"] += peso / (k_rrf + rank + 1)
        ordenados = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
        return [item["doc"] for item in ordenados[: self.k]]

    def invoke(self, query):
        """
        Interfaz principal. Detecta automáticamente si la consulta
        contiene un ID estructurado y elige la estrategia óptima.
        """
        # ── Nivel 1: ¿Hay un ID exacto en la pregunta? ────────────────────
        match = PATRON_IDS.search(query)
        if match:
            id_completo = match.group(0).upper()   # ej: "GST-003"
            prefijo = match.group(1).upper()        # ej: "GST"

            doc_directo = _buscar_id_en_csv(id_completo, prefijo, self.csvs)
            if doc_directo:
                print(f"  [SmartRetriever] ✓ ID '{id_completo}' encontrado por búsqueda directa.")
                # Completamos con resultados semánticos si quedan slots
                docs_vector = self.vector_retriever.invoke(query)
                resultados = [doc_directo] + [
                    d for d in docs_vector
                    if d.page_content != doc_directo.page_content
                ][: self.k - 1]
                return resultados
            else:
                print(f"  [SmartRetriever] ID '{id_completo}' no encontrado en CSVs → modo híbrido.")

        # ── Niveles 2+3: Búsqueda Híbrida BM25 + Vector ──────────────────
        docs_bm25 = self.bm25_retriever.invoke(query)
        docs_vector = self.vector_retriever.invoke(query)
        return self._rrf(
            [docs_bm25, docs_vector],
            [self.peso_bm25, self.peso_vector]
        )

    def get_relevant_documents(self, query):
        """Alias de compatibilidad con cadenas LangChain antiguas."""
        return self.invoke(query)


# ─────────────────────────────────────────────────────────────────
# FUNCIÓN PÚBLICA DE INICIALIZACIÓN
# ─────────────────────────────────────────────────────────────────

def crear_retriever_hibrido(
    chroma_db_path="./chroma_db",
    fragmentos_path="./fragmentos_bm25.pkl",
    directorio_datos="./data",
    k=3,
    peso_bm25=0.5,
    peso_vector=0.5
):
    """
    Inicializa el SmartHybridRetriever listo para usar.

    Args:
        chroma_db_path:    Ruta a la carpeta de ChromaDB.
        fragmentos_path:   Ruta al archivo .pkl con fragmentos para BM25.
        directorio_datos:  Carpeta raíz donde están los CSV originales.
        k:                 Número de documentos a recuperar.
        peso_bm25:         Peso del retriever BM25 en la fusión RRF (0.0-1.0).
        peso_vector:       Peso del retriever vectorial en la fusión RRF (0.0-1.0).

    Returns:
        SmartHybridRetriever listo para usar como drop-in replacement.
    """

    # ── Cargar CSVs en memoria para búsquedas directas por ID ────────────
    print("  [SmartRetriever] Cargando CSVs para búsqueda directa por ID...")
    csvs_cargados = _encontrar_csvs(directorio_datos)
    print(f"  [SmartRetriever] {len(csvs_cargados)} CSV(s) cargados: "
          f"{[os.path.basename(r) for r in csvs_cargados]}")

    # ── Retriever Vectorial (ChromaDB) ────────────────────────────────────
    print("  [SmartRetriever] Conectando con ChromaDB...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={'device': 'cuda'}
    )
    vectorstore = Chroma(persist_directory=chroma_db_path, embedding_function=embeddings)
    vector_retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    # ── Retriever BM25 (Léxico) ───────────────────────────────────────────
    print("  [SmartRetriever] Cargando índice BM25...")
    try:
        with open(fragmentos_path, "rb") as f:
            fragmentos = pickle.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"No se encontró '{fragmentos_path}'.\n"
            "Ejecuta crear_bd.py primero para generar el archivo de fragmentos BM25."
        )
    bm25_retriever = BM25Retriever.from_documents(fragmentos)
    bm25_retriever.k = k

    # ── Ensamblar el retriever inteligente ────────────────────────────────
    retriever = SmartHybridRetriever(
        bm25_retriever=bm25_retriever,
        vector_retriever=vector_retriever,
        csvs_cargados=csvs_cargados,
        k=k,
        peso_bm25=peso_bm25,
        peso_vector=peso_vector
    )

    print(f"  [SmartRetriever] ✓ Listo — ID directo | BM25={peso_bm25} | Vector={peso_vector} | k={k}")
    return retriever
