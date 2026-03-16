import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# We will read this from the `.env` file!
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_prediction(analyst_name, hot_numbers, past_animals, play_type, target_lottery, dream_keyword, todays_results, enjaulados=None, internet_consensus=None):
    """
    Motor Híbrido V2: Combina análisis estadístico (Poisson, Markov), Varianza, Consenso, y heurística lúdica venezolana.
    """
    if not GEMINI_API_KEY:
         print("Error crítico: GEMINI_API_KEY no encontrada.")

    # Fecha y hora actual para el motor de Frecuencia Horaria
    ahora = datetime.now()
    fecha_str = ahora.strftime("%Y-%m-%d")
    hora_str = ahora.strftime("%I:%M %p")

    # Formateo de resultados globales (Scraper)
    results_str = "No hay resultados previos hoy."
    if todays_results and isinstance(todays_results, dict):
        parts = []
        for lottery_name, results in todays_results.items():
            if results:
                lot_res = ", ".join([f"{r['schedule']}: {r['animal']}" for r in results])
                parts.append(f"{lottery_name} -> {lot_res}")
        if parts:
            results_str = " | ".join(parts)

    # Formateo de secuencia manual retrospectiva
    sequence_str = "Sin historial secuencial ingresado."
    if past_animals and len(past_animals) > 0:
        sequence_str = " -> ".join(past_animals)
        results_str = "[IGNORADO] Secuencia manual forzada. Priorizar la secuencia sobre el ecosistema global."

    # Reglas Matemáticas Estrictas según el tipo de jugada
    play_rules = ""
    if play_type == "Quiniela":
        play_rules = """
        [REGLAS DE QUINIELA]: Debes entregar EXACTAMENTE 6 animales. Evalúa la 'Ley de Tercios' sobre los sorteos de las 08:00 AM y 09:00 AM. 
        Calcula probabilidades asumiendo apuesta simultánea en 3 loterías (Lotto Activo, Granjita, Ruleta Activa).
        """
    elif play_type == "Tripleta":
        play_rules = """
        [REGLAS DE TRIPLETA]: Debes entregar EXACTAMENTE 3 animales de altísima confianza. Busca convergencia entre Números Espejo y Nodos Piramidales.
        """

    # Format Enjaulados (Varianza)
    enjaulados_str = "Ninguno"
    if enjaulados and len(enjaulados) > 0:
        enjaulados_str = ", ".join(enjaulados)
        
    # Format Internet Consensus
    consensus_str = "Sin datos de consenso hoy"
    if internet_consensus and len(internet_consensus) > 0:
        consensus_str = ", ".join(internet_consensus)
        
    system_instruction = f"""
    CONTEXTO Y ROL: Eres "Oráculo Activo V2", una IA predictiva de grado casino, especializada en la ruleta de 38 figuras de Venezuela. Analista a cargo: '{analyst_name}'.
    Fecha de Operación: {fecha_str} | Hora Actual: {hora_str}
    
    MOTORES DE ANÁLISIS AVANZADO (Ejecución Obligatoria):
    
    1. LEY DE LOS TERCIOS Y DISTRIBUCIÓN DE POISSON:
       - No busques solo "animales que no han salido". Si la secuencia muestra un número repetido, el algoritmo de la ruleta está en fase de repetición. Sugiere al menos 1 "Repetidor Caliente" del día.
       
    2. SIMETRÍA Y NÚMEROS ESPEJO:
       - Cuando sale un número, su inverso tiene alta probabilidad de salir en las próximas 3 horas.
       - Espejos principales: 01<->10, 02<->20, 03<->30, 12<->21, 13<->31, 23<->32, 14<->not posible(41 no existe, usa 14->04->Alacrán).
       
    3. ANÁLISIS DE CUADRANTES BIOLÓGICOS (Detección de Sesgo Algorítmico):
       - Identifica qué grupo domina hoy la secuencia:
         * Domésticos: Perro, Gato, Vaca, Caballo, Gallo, Gallina, Cerdo, Carnero.
         * Salvajes: León, Tigre, Elefante, Jirafa, Cebra, Mono, Zorro, Oso.
         * Acuáticos: Delfín, Ballena, Pescado, Caimán.
         * Aves: Águila, Perico, Paloma, Pavo, Zamuro.
       - Si hoy están saliendo muchas Aves, tu predicción debe incluir un Ave rezagada.

    4. CADENAS DE MARKOV ("Jalados" Clásicos):
       - 0 (Delfín) jala 16, 33, 00. | 00 (Ballena) jala 0, 30, 24, 33, 27.
       - 5 (León) jala 10, 11, 29, 12. | 10 (Tigre) jala 23, 32, 01, 19.
       - 36 (Culebra) jala 24, 19, 08, 15.
       
    5. FRECUENCIA HORARIA:
       - Sorteos AM (09:00 - 12:00): Favorecen animales de granja/domésticos y números bajos (00 al 15).
       - Sorteos PM (13:00 - 19:00): Favorecen animales salvajes y números altos (16 al 36).
       - Ajusta tus pesos probabilísticos según la "Hora Actual" provista.

    6. REDUCCIÓN MODULAR (Pirámide), SUEÑOS, VARIANZA Y CONSENSO: 
       - Cruza los nodos ingresados por el usuario con el Diccionario Onírico estándar.
       - Animales Enjaulados Hoy (Varianza Confirmada Externamente): {enjaulados_str}
       - Consenso de Internet (Sentimiento Global): {consensus_str}

    TONO: Experto en estadística, crupier veterano y analista de datos lúdicos. Seguro y analítico.
    Lotería Objetivo: {target_lottery}
    {play_rules}

    ESTRUCTURA JSON REQUERIDA Y ESTRICTA:
    {{
        "analysis_meta": {{
            "dominant_quadrant": "Nombre del cuadrante biológico dominante",
            "hot_mirror": "Número espejo detectado (si aplica)",
            "confidence_score": "XX%"
        }},
        "primary_play": {{ "combination": [{{"number": "XX", "animal": "Nombre"}}], "probability": "XX%" }},
        "secondary_plays": [
            {{ "combination": [{{"number": "XX", "animal": "Nombre"}}], "probability": "XX%" }}
        ],
        "reasoning": "Explicación técnica usando los 6 motores. Termina OBLIGATORIAMENTE con la advertencia: 'Recuerda que estos análisis optimizan tus estrategias mediante estadística e historia, pero el Lotto Activo es un juego gobernado por el azar algorítmico certificado (2,63% de prob.). Juega con responsabilidad.'"
    }}
    """

    user_prompt = f"""
    EJECUCIÓN DE ANÁLISIS ORÁCULO V2:
    - Lotería: {target_lottery}
    - Nodos (Pirámide): {hot_numbers}
    - Secuencia Hoy: {sequence_str}
    - Metadato Onírico: {dream_keyword if dream_keyword else "Ninguno"}
    - Ecosistema Global: {results_str}
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.5,
            "responseMimeType": "application/json"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=45)
        response.raise_for_status()
        
        data = response.json()
        # The response is now cleanly returned as JSON due to responseMimeType="application/json"
        raw_content = data['candidates'][0]['content']['parts'][0]['text']
        return json.loads(raw_content.strip())
        
    except requests.exceptions.HTTPError as e:
        print(f"Error calling AI-ASR: {e}")
        if response is not None:
             print(f"Response text: {response.text}")
        return {
           "analysis_meta": {"dominant_quadrant": "N/A", "hot_mirror": "N/A", "confidence_score": "0%"},
           "primary_play": { "combination": [{"number": "00", "animal": "Ballena"}], "probability": "45%" },
           "secondary_plays": [
               { "combination": [{"number": "1", "animal": "Carnero"}], "probability": "30%" },
               { "combination": [{"number": "2", "animal": "Toro"}], "probability": "25%" }
           ],
           "reasoning": f"Estimado {analyst_name}: El núcleo AI-ASR experimentó fallo de red o latencia extrema. Esta es una proyección de supervivencia local."
       }

if __name__ == "__main__":
    res = get_ai_prediction("Tester", ["1", "5"], ["[La Granjita] 08:00 AM - Delfín", "[Lotto Activo] 09:00 AM - Ballena"], "Quiniela", "Agua", [], [], [])
    print(json.dumps(res, indent=2))
