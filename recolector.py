# --- Este es el archivo: recolector.py ---
# (Se ejecuta en ~/SS91-V3)

import asyncio
import os
import requests
import json
import numpy as np
from datetime import datetime
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer

# --- 1. CONFIGURACIÓN ---
# (Recuerda hacer 'export' de tus claves en la terminal)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")

try:
    supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    print("[RECOLECTOR] Iniciado. Conectado a Supabase.")
except Exception as e:
    print(f"ERROR: No se pudo iniciar. Revisa tus variables de entorno. {e}")
    exit()


# --- 2. TUS FUNCIONES DE BÚSQUEDA ---
# (Reutilizamos la lógica de tu 'market-analyzer')

async def LLAMAR_BUSCADOR_WEB(consulta: str) -> list:
    """Busca en la web usando SerpAPI."""
    print(f"    Buscando: {consulta}")
    try:
        url = f"https://serpapi.com/search.json?q={consulta}&api_key={SERPAPI_KEY}"
        # Usamos requests síncrono para simplicidad
        response = requests.get(url).json()
        results = [
            {"type": "web", "content": f"{item['title']} {item.get('snippet', '')}", "score": 0.7}
            for item in response.get("organic_results", [])[:3]
        ]
        return results
    except Exception as e:
        print(f"    ERROR en buscador web: {e}")
        return []

def COMBINAR_Y_FILTRAR(resultados_web: list, consulta: str) -> list:
    """Correlaciona y filtra resultados usando embeddings."""
    if not resultados_web: return []
    try:
        query_embedding = embedder.encode(consulta)
        for item in resultados_web:
            item_embedding = embedder.encode(item["content"])
            # Calculamos la similitud coseno
            similarity = np.dot(item_embedding, query_embedding) / (
                np.linalg.norm(item_embedding) * np.linalg.norm(query_embedding)
            )
            item["score"] = item["score"] * similarity
        resultados_web.sort(key=lambda x: x["score"], reverse=True)
        return resultados_web
    except Exception as e:
        print(f"    ERROR en filtrado: {e}")
        return resultados_web

# --- 3. LÓGICA DEL RECOLECTOR ---
SEÑALES_DE_ADVERTENCIA_SS91 = [
    {'id': 'f1', 'consulta': 'sentimiento twitter eurusd negativo'},
    {'id': 'f2', 'consulta': 'flujo capital minorista eurusd comprando'},
    {'id': 'f3', 'consulta': 'pico busquedas google "crisis financiera"'},
    {'id': 'f5', 'consulta': 'noticias ciberataque bancos centrales'},
    # TODO: Añade aquí las otras 41 señales
]

async def ejecutar_recolector_ss91():
    print("--- INICIANDO RECOLECCIÓN SS91 ---")
    for señal in SEÑALES_DE_ADVERTENCIA_SS91:
        id_factor, consulta = señal['id'], señal['consulta']
        print(f"  [Buscando Señal: {id_factor}]...")
        
        resultados_web = await LLAMAR_BUSCADOR_WEB(consulta) 
        resultados_filtrados = COMBINAR_Y_FILTRAR(resultados_web, consulta)
        
        señal_detectada = False
        # Umbral de confianza (puedes ajustarlo)
        if resultados_filtrados and resultados_filtrados[0]['score'] > 0.75: 
             señal_detectada = True
        
        if señal_detectada:
            print(f"    > ¡SEÑAL DETECTADA! Guardando en Supabase...")
            try:
                # Guardamos en la tabla que creamos
                supabase_client.table('eventos_ss91').insert({ 
                    'factor_id': id_factor,
                    'detectado_en': datetime.now().isoformat()
                }).execute()
            except Exception as e:
                print(f"    > ERROR al guardar: {e}")
        else:
            print("    > No detectada.")
    print("--- RECOLECCIÓN COMPLETADA ---")

if __name__ == "__main__":
    if not all([SUPABASE_URL, SUPABASE_KEY, SERPAPI_KEY]):
        print("ERROR: Faltan variables de entorno (SUPABASE_URL, SUPABASE_KEY, SERPAPI_KEY).")
    else:
        asyncio.run(ejecutar_recolector_ss91())

