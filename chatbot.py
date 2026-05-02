from langchain_community.llms import LlamaCpp
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from hybrid_retriever import crear_retriever_hibrido

print("Inicializando sistemas... (esto puede tardar unos segundos)")

# 1. Retriever Inteligente (ID directo + BM25 + Vectorial)
# - Si la pregunta contiene un ID (GST-003, CLI-0049, EMP-0001) → búsqueda directa en CSV
# - Si no → Retriever Híbrido BM25 + Vectorial con RRF
retriever = crear_retriever_hibrido(k=3, peso_bm25=0.5, peso_vector=0.5, directorio_datos="./data")

# 2. Cargar el modelo
RUTA_MODELO = "../llama.cpp/gemma-2-2b-it-Q4_K_M.gguf"

llm = LlamaCpp(
    model_path=RUTA_MODELO,
    n_gpu_layers=99,
    n_ctx=2048,
    n_batch=512,   # FIX: añadido para mejor uso de la GPU
    f16_kv=True,
    verbose=False,
    temperature=0.1
)

# 3. Prompt
template = """Usa los siguientes fragmentos de contexto de la empresa para responder a la pregunta del trabajador de forma clara y amable.
Si no sabes la respuesta basándote estrictamente en el contexto, di simplemente que no tienes esa información. NO inventes datos.

Contexto recuperado de los documentos:
{context}

Pregunta del trabajador: {question}

Respuesta del Asistente:"""
prompt = PromptTemplate(template=template, input_variables=["context", "question"])

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 4. Cadena — el retriever se llama UNA sola vez y el resultado se reutiliza
#    FIX: antes se llamaba retriever.invoke() dos veces por pregunta
#    (una en la cadena y otra para mostrar fuentes), doblando el trabajo.
qa_chain = (
    RunnablePassthrough.assign(
        context=lambda x: format_docs(retriever.invoke(x["question"])),
        docs=lambda x: retriever.invoke(x["question"])
    )
    | RunnablePassthrough.assign(
        result=(
            lambda x: (prompt | llm | StrOutputParser()).invoke(
                {"context": x["context"], "question": x["question"]}
            )
        )
    )
)

# 5. Interfaz del Chat
print("\n" + "="*60)
print("Chatbot de Empresa Iniciado (Escribe 'salir' para terminar)")
print("="*60 + "\n")

while True:
    pregunta = input("Tú (Trabajador): ")
    if pregunta.lower() in ['salir', 'exit', 'quit']:
        print("Cerrando sesión. ¡Hasta pronto!")
        break

    print("Buscando en los documentos y pensando...")

    # FIX: una sola invocación — docs y respuesta salen del mismo chain
    output = qa_chain.invoke({"question": pregunta})
    docs = output["docs"]
    respuesta = output["result"]

    print(f"\nAsistente: {respuesta}\n")

    print("[Fuentes consultadas:]")
    for doc in docs:
        nombre_archivo = doc.metadata.get('source', 'Desconocido').split('/')[-1]
        print(f" - {nombre_archivo}")
    print("-" * 60 + "\n")