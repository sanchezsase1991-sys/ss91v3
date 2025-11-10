from ss91_v3.utils import log
from sherloock import Sherloock # Importas tu motor
import json
import numpy as np

# Instancia tu motor de razonamiento
SHERLOOCK_ENGINE = Sherloock() 

def generate_decision():
    try:
        # 1. LEER LOS DATOS
        with open("results/snapshots/snapshot.json", "r") as f:
            snapshot_data = json.load(f)

        # 2. EXTRAER FACTORES REALES
        rsi = snapshot_data['ohlc'].get('RSI_14', 50)
        sentimiento = snapshot_data['marginal_factors'].get('vader_sentiment', 0)
        precios_recientes = snapshot_data['ohlc'].get('recent_prices', [1.05, 1.06])
        soporte_fibo = snapshot_data['fibo'].get('nearest_support_level', 1.0)
        
        # 3. IMPLEMENTAR ESTRATEGIA (El "Traductor")
        # Aquí plasmas tu "Investigación"
        comando_para_sherloock = ""
        context_msg = "Evaluando..."

        if rsi < 30 and sentimiento < 0.3:
            # Estrategia: Sobreventa y pánico. Usar PuLP para optimizar la entrada.
            context_msg = f"Sobreventa (RSI: {rsi}) y Pánico (Sent: {sentimiento}). Optimizando entrada."
            comando_para_sherloock = f"forecast {precios_recientes} with_limit {soporte_fibo}"
        
        elif rsi > 70 and sentimiento > 0.8:
            # Estrategia: Euforia. Usar Z3 para verificar restricciones.
            context_msg = "Euforia detectada. Verificando restricciones lógicas."
            comando_para_sherloock = "solve parallel euforia where x > 10" # Ejemplo
        
        else:
            # Estrategia: Mercado normal, no operar.
            decision_raw = "HOLD"
            context_msg = "Mercado en rango. Sin señal."

        # 4. LLAMAR A SHERLOOCK (si hay un comando)
        if comando_para_sherloock:
            respuesta_sherloock = SHERLOOCK_ENGINE.reason(comando_para_sherloock)
            decision_raw = interpretar_respuesta_sherloock(respuesta_sherloock)
            context_msg = f"{context_msg} | Sherloock: {respuesta_sherloock}"

        # ... (resto de tu código para guardar el record) ...
        
        opp_text = f"RSI: {rsi}, Sent: {sentimiento}"
        decision_record = { ... } # Tu registro de decisión
        
        return decision_record, decision_raw, opp_text, context_msg

    except Exception as e:
        log.error(f"Decision generation failed: {e}")
        raise

def interpretar_respuesta_sherloock(respuesta: str) -> str:
    # Esta es la pieza final: traduce la respuesta de Sherloock
    if "[FORECAST PuLP]" in respuesta:
        # Aquí extraes el valor pronosticado y decides
        return "BUY" # Ejemplo
    if "[MÚSCULO LÓGICO]" in respuesta:
        return "SELL" # Ejemplo
    return "HOLD"
