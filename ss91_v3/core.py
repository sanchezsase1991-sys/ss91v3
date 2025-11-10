import os
import json
import datetime
import re
from ss91_v3.utils import log
from sherloock import Sherloock  # Importa tu IA desde el paquete instalado

# Instanciamos el motor de razonamiento UNA SOLA VEZ.
# (sherloock cargará sus modelos internos aquí)
try:
    SHERLOOCK_ENGINE = Sherloock()
    log.info("Motor de razonamiento Sherloock inicializado.")
except Exception as e:
    log.error(f"Error fatal: No se pudo inicializar Sherloock. {e}")
    # Si Sherloock no carga, creamos una instancia 'None'
    SHERLOOCK_ENGINE = None

def generate_decision():
    """
    Esta es la función principal del "Traductor".
    1. Lee los datos del snapshot.
    2. Aplica la lógica de "El Santo Grial".
    3. Formula un comando para Sherloock.
    4. Interpreta la respuesta de Sherloock.
    """
    log.info("Iniciando el 'Traductor Estratégico' (core.py)...")
    
    if SHERLOOCK_ENGINE is None:
        log.error("Sherloock no está disponible. Abortando decisión.")
        raise ImportError("El motor Sherloock no pudo ser inicializado.")

    # 1. LEER LOS DATOS DEL SNAPSHOT
    # (El .yml del Paso 2 asegura que este archivo exista)
    today = datetime.date.today().isoformat()
    snapshot_path = os.path.join("results", "snapshots", f"{today}.json")
    
    try:
        with open(snapshot_path, "r") as f:
            data = json.load(f)
            log.info(f"Snapshot '{snapshot_path}' cargado exitosamente.")
    except FileNotFoundError:
        log.error(f"Error Crítico: No se encontró el snapshot '{snapshot_path}'.")
        raise
    except json.JSONDecodeError:
        log.error(f"Error Crítico: El snapshot '{snapshot_path}' está corrupto.")
        raise

    # 2. EXTRAER LOS FACTORES (Gasolina)
    # Extraemos los datos de forma segura usando .get()
    ohlc = data.get('ohlc_latest', {})
    fibo = data.get('fibonacci', {})
    marginals = data.get('marginal_factors', {})

    # Factores clave para la estrategia
    rsi = ohlc.get('RSI_14', 50.0)
    fibo_ratio = fibo.get('position_ratio', 0.5) # 0.0=Mínimo 1A, 1.0=Máximo 1A
    sentimiento = marginals.get('reddit_vader_avg', 0.5) # 0.0=Pánico, 1.0=Euforia
    gtrends_crisis = marginals.get('gtrends_recession', 0.0)
    
    # Este 'recent_prices' lo añadiremos en el Paso 3.B
    precios_recientes = ohlc.get('recent_prices', [ohlc.get('close', 1.05)])
    soporte_fibo = fibo.get('low_1y', 1.0) # El soporte más fuerte

    # 3. APLICAR LA ESTRATEGIA (Formular el Comando)
    comando_para_sherloock = ""
    context_msg = "Evaluando..."
    decision_raw = "HOLD" # Por defecto
    opp_text = "Sin ejecución de Sherloock."

    # --- Estrategia 1: Pánico y Sobreventa Extrema ---
    if rsi < 30 and fibo_ratio < 0.2 and sentimiento < 0.35 and gtrends_crisis > 0.5:
        context_msg = f"Pánico Detectado (RSI:{rsi:.0f}, Fibo:{fibo_ratio:.2f}, Sent:{sentimiento:.2f}). Optimizando entrada (PuLP)."
        # Usamos el optimizador PuLP de Sherloock para encontrar la mejor entrada
        # por encima del soporte del último año.
        comando_para_sherloock = f"forecast {precios_recientes} with_limit {soporte_fibo}"

    # --- Estrategia 2: Euforia y Sobrecompra Extrema ---
    elif rsi > 70 and fibo_ratio > 0.8 and sentimiento > 0.8:
        context_msg = f"Euforia Detectada (RSI:{rsi:.0f}, Fibo:{fibo_ratio:.2f}, Sent:{sentimiento:.2f}). Verificando restricción (Z3)."
        # Usamos el motor lógico Z3 de Sherloock para verificar una "Crisis de Credibilidad"
        # (Este es un ejemplo, puedes refinar la lógica de Z3)
        comando_para_sherloock = "solve parallel euforia_check where x > 100"

    # --- Estrategia 3: Mercado en Rango ---
    else:
        context_msg = f"Mercado en Rango (RSI:{rsi:.0f}, Fibo:{fibo_ratio:.2f}). Sin señal."
        decision_raw = "HOLD"

    # 4. LLAMAR A SHERLOOCK (El Motor)
    if comando_para_sherloock:
        log.info(f"Ejecutando comando para Sherloock: {comando_para_sherloock}")
        try:
            respuesta_sherloock = SHERLOOCK_ENGINE.reason(comando_para_sherloock)
            log.info(f"Respuesta de Sherloock: {respuesta_sherloock}")
            
            # 5. INTERPRETAR RESPUESTA
            decision_raw, opp_text = interpretar_respuesta_sherloock(respuesta_sherloock, ohlc.get('close', 1.05))
            context_msg = f"{context_msg} | Sherloock: {respuesta_sherloock}"
        
        except Exception as e:
            log.error(f"Sherloock.reason() falló: {e}")
            decision_raw = "HOLD"
            context_msg = "Error al ejecutar el motor de razonamiento."
            opp_text = str(e)

    # 6. FORMATEAR SALIDA
    decision_record = {
        "symbol": "EURUSD=X",
        "timestamp_utc": str(datetime.datetime.utcnow()),
        "decision": decision_raw,
        "context": context_msg,
        "sherloock_output": opp_text,
        "data_used": {
            "rsi": rsi,
            "fibo_ratio": fibo_ratio,
            "sentiment": sentimiento,
            "gtrends_crisis": gtrends_crisis
        }
    }
    
    return decision_record, decision_raw, opp_text, context_msg

def interpretar_respuesta_sherloock(respuesta: str, precio_actual: float) -> tuple[str, str]:
    """
    Traduce la respuesta de texto de Sherloock a una decisión de trading.
    """
    try:
        if "[FORECAST PuLP]" in respuesta:
            # Intenta extraer el valor optimizado
            match = re.search(r'optimizado: ([\d\.]+)', respuesta)
            if match:
                valor_optimizado = float(match.group(1))
                # Si el punto de entrada optimizado es más bajo que el actual, es una señal de compra
                if valor_optimizado < precio_actual:
                    return "BUY", f"PuLP sugiere entrada óptima en {valor_optimizado:.5f}"
                else:
                    return "HOLD", f"PuLP ( {valor_optimizado:.5f}) no mejora el precio actual"
            else:
                return "HOLD", "PuLP no pudo optimizar la entrada."

        elif "[MÚSCULO LÓGICO]" in respuesta:
            # Intenta ver si Z3 encontró soluciones (señal de "crisis")
            match = re.search(r'(\d+) soluciones', respuesta)
            if match and int(match.group(1)) > 0:
                # Si Z3 encuentra soluciones, confirma nuestra teoría de "Euforia = Venta"
                return "SELL", "Z3 confirmó restricción de euforia (Venta)."
            else:
                return "HOLD", "Z3 no encontró restricción de euforia."

    except Exception as e:
        log.warning(f"Error al interpretar respuesta de Sherloock: {e}")
        return "HOLD", str(e)
    
    return "HOLD", "Respuesta de Sherloock no concluyente."
