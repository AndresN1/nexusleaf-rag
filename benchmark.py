import pandas as pd
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from langchain_community.llms import LlamaCpp
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from hybrid_retriever import crear_retriever_hibrido

print("Cargando el motor para el Benchmark...")

# ─────────────────────────────────────────────
# 1. Cargar Base de datos y Modelo
# ─────────────────────────────────────────────

# Retriever Inteligente: ID directo (pandas) + BM25 (léxico) + Vectorial (semántico)
# Si la pregunta contiene un ID exacto (GST-003, CLI-0049, EMP-0001) → búsqueda directa
# Si no → Retriever Híbrido con Reciprocal Rank Fusion
retriever = crear_retriever_hibrido(k=3, peso_bm25=0.5, peso_vector=0.5, directorio_datos="./data")

RUTA_MODELO = "../llama.cpp/gemma-2-2b-it-Q4_K_M.gguf"
llm = LlamaCpp(
    model_path=RUTA_MODELO,
    n_gpu_layers=99,
    n_ctx=2048,
    n_batch=512,      # FIX: batch grande → la GPU procesa más tokens por ciclo
    f16_kv=True,
    verbose=False,
    temperature=0.0
)

template = """Usa los siguientes fragmentos de contexto de la empresa para responder a la pregunta de forma clara y amable.
Si no sabes la respuesta basándote estrictamente en el contexto, di "NO_INFO".

Contexto:
{context}

Pregunta: {question}

Respuesta:"""
prompt = PromptTemplate(template=template, input_variables=["context", "question"])

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

chain = (
    RunnablePassthrough.assign(
        context=lambda x: format_docs(retriever.invoke(x["question"])),
        source_documents=lambda x: retriever.invoke(x["question"])
    )
    | RunnablePassthrough.assign(
        result=(prompt | llm | StrOutputParser())
    )
)

# ─────────────────────────────────────────────
# 2. Cargar preguntas
# ─────────────────────────────────────────────

df_preguntas = pd.read_csv("preguntas_benchmark.csv")
total = len(df_preguntas)
print(f"Iniciando evaluación de {total} preguntas...\n")

# ─────────────────────────────────────────────
# 3. Bucle con concurrencia controlada
#
#    FIX PRINCIPAL: antes se lanzaban N preguntas a la vez sin límite,
#    saturando la CPU. Ahora un semáforo limita a MAX_WORKERS tareas
#    simultáneas. LlamaCpp no es thread-safe para inferencia paralela,
#    así que usamos ThreadPoolExecutor con 1 worker para la GPU y
#    paralelizamos solo el retrieval (que sí es seguro).
# ─────────────────────────────────────────────

MAX_WORKERS = 4          # Hilos paralelos para retrieval en ChromaDB
SEMAPHORE_LLM = 1        # LlamaCpp: solo 1 inferencia a la vez (limitación de llama.cpp)

resultados = []
lock = asyncio.Lock()    # Para escribir en resultados de forma segura

def run_retrieval(pregunta):
    """Retrieval paralelizable — ChromaDB lo soporta con hilos."""
    docs = retriever.invoke(pregunta)
    return docs, format_docs(docs)

async def evaluar_pregunta(semaforo_llm, executor, index, pregunta):
    loop = asyncio.get_event_loop()

    # Retrieval en paralelo (no bloquea el event loop)
    docs, contexto = await loop.run_in_executor(executor, run_retrieval, pregunta)

    inicio = time.time()

    # LlamaCpp solo admite 1 inferencia simultánea → semáforo con límite 1
    async with semaforo_llm:
        output = await loop.run_in_executor(
            None,
            lambda: (prompt | llm | StrOutputParser()).invoke(
                {"context": contexto, "question": pregunta}
            )
        )

    tiempo_total = round(time.time() - inicio, 2)

    fuentes = ", ".join([doc.metadata.get('source', '').split('/')[-1] for doc in docs])
    contextos_usados = "\n---\n".join([doc.page_content for doc in docs])

    print(f"[{index+1}/{total}] ✓ ({tiempo_total}s) {pregunta[:60]}...")

    return {
        "Pregunta": pregunta,
        "Respuesta_Gemma": output.strip(),
        "Tiempo_Segundos": tiempo_total,
        "Fuentes_Consultadas": fuentes,
        "Textos_Recuperados": contextos_usados
    }

async def main():
    semaforo_llm = asyncio.Semaphore(SEMAPHORE_LLM)

    # ThreadPoolExecutor solo para el retrieval paralelo
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tareas = [
            evaluar_pregunta(semaforo_llm, executor, i, fila['pregunta'])
            for i, fila in df_preguntas.iterrows()
        ]
        # gather ejecuta las tareas concurrentemente pero el semáforo
        # garantiza que solo 1 llega al LLM a la vez
        resultados_raw = await asyncio.gather(*tareas)

    return list(resultados_raw)

# ─────────────────────────────────────────────
# 4. Ejecutar y guardar
# ─────────────────────────────────────────────

resultados = asyncio.run(main())

df_resultados = pd.DataFrame(resultados)
df_resultados.to_csv("resultados_benchmark.csv", index=False, encoding='utf-8')

print("\n¡Benchmark completado! Revisa el archivo 'resultados_benchmark.csv'")