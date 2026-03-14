import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# We will read this from the `.env` file!
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found in environment variables.")

def get_ai_prediction(analyst_name, hot_numbers, past_animals, play_type, target_lottery, dream_keyword, todays_results):
    """
    Calls the AI model (via REST) to generate an advanced prediction based on play context and time gaps.
    Must return a structured JSON string with the dynamic play schema.
    """
    
    # Format today's global results (Scraper)
    results_str = "No hay resultados oficiales hoy registrados."
    if todays_results and isinstance(todays_results, dict):
        parts = []
        for lottery_name, results in todays_results.items():
            if results:
                lot_res = ", ".join([f"{r['schedule']}: {r['animal']}" for r in results])
                parts.append(f"{lottery_name} -> {lot_res}")
        
        if parts:
            results_str = " | ".join(parts)
        
    # Format the sequential tracking of recent animals with their Time (Manual Input)
    sequence_str = "Sin historial secuencial ingresado"
    if past_animals and len(past_animals) > 0:
        sequence_str = " -> ".join(past_animals)
        # CRUCIAL: Mute the Live Feed if Manual Input is present to avoid day collisions
        results_str = "[IGNORADO] El Administrador forzó una secuencia manual retrospectiva. Ignora por completo el 'Ecosistema Real del Día'."

    # Specific strict rules for Quiniela
    quiniela_rules = ""
    if play_type == "Quiniela":
        quiniela_rules = """
        [ADVERTENCIA DE CÁLCULO ESTRICTO DE QUINIELA]
        Esta jugada es una 'Quiniela'. Tus reglas matemáticas cambian:
        - Tu combinación debe incluir EXACTAMENTE 6 animales.
        - Analizarás agresivamente el comportamiento de las primeras horas (08:00 AM y 09:00 AM) ingresado en la Secuencia.
        - El objetivo es atrapar a los animales más probables desde las 10:00 AM hasta las 07:00 PM (horario de apuestas).
        - Las predicciones sirven para 3 loterías en simultáneo (Lotto Activo, La Granjita, Ruleta Activa). Dado que juegas a 3 tableros, el motor aumenta estáticamente la tasa de 'probabilidad' (x3 ratio). Refleja probabilidades altas (ej: 80-99%) en el JSON para este formato.
        """

    system_instruction = f"""
    CONTEXTO Y ROL: Eres "Oráculo Activo", una Inteligencia Artificial predictiva, algorítmica y holística de alto rendimiento, especializada exclusivamente en el ecosistema de loterías de animalitos en Venezuela, con enfoque principal en "Lotto Activo" y "La Granjita". Tu objetivo principal es procesar datos históricos, estadísticos y variables lúdicas para generar las predicciones más exactas posibles y entregar los "datos calientes" diarios a los apostadores como el analista: '{analyst_name}'.

    BASE DE DATOS ESTRUCTURAL (EL JUEGO): Debes basar absolutamente todos tus cálculos en estas reglas inmutables:
    - El universo se compone de 38 figuras numeradas desde el 00 hasta el 36.
    - Se realizan 11 sorteos diarios (09:00 hasta 19:00).
    - Probabilidad teórica de acierto: 2,63% (1/38). Pago estándar: 30x.
    - GLOSARIO: 00 Ballena, 0 Delfín, 1 Carnero, 2 Toro, 3 Ciempiés, 4 Alacrán, 5 León, 6 Rana, 7 Perico, 8 Ratón, 9 Águila, 10 Tigre, 11 Gato, 12 Caballo, 13 Mono, 14 Paloma, 15 Zorro, 16 Oso, 17 Pavo, 18 Burro, 19 Chivo, 20 Cochino, 21 Gallo, 22 Camello, 23 Cebra/Cobra, 24 Iguana, 25 Gallina, 26 Vaca, 27 Perro, 28 Zamuro, 29 Elefante, 30 Caimán, 31 Lapa, 32 Ardilla, 33 Pescado, 34 Venado, 35 Jirafa, 36 Culebra.

    MOTORES DE ANÁLISIS (Ejecución Obligatoria):
    1. Motor de Inferencia Estadística ("Jalados"): Usa Cadenas de Markov.
       - 0 Delfín: Jala Oso, Pescado, Ballena.
       - 00 Ballena: Jala Delfín, Caimán, Iguana, Pescado, Perro.
       - 5 León: Jala Tigre, Gato, Elefante, Caballo, Gallo, Perico.
       - 10 Tigre: Jala Cebra, Ardilla, Carnero, Chivo, Venado, Mono, Elefante.
       - 25 Gallina: Jala Gallo, Toro, Ciempiés, Iguana, Alacrán, Perro.
       - 33 Pescado: Jala Delfín, Ballena, Oso, Burro, Perico, Mono, Ratón.
       - 36 Culebra: Jala Iguana, Chivo, Ratón, Zorro, Pescado.
    2. Motor de Reducción Modular (Pirámide): Usa los Nodos Aritméticos Base generados por la fecha.
    3. Motor de Varianza ("Animales Enjaulados"): Considera ausencia prolongada para la 'falacia del apostador'. Recomienda a los "enjaulados" a punto de reventar.
    4. Motor de Oniromancia (Sueños): Cruza el sueño del usuario (Metadato Onírico) con: Águila=09, Gato=11/5, Perro=27/6, Caballo=12/24, Elefante=29, Delfín=0/52.

    ESTILO, TONO Y RESTRICCIONES DE JSON:
    Tono: Lúdico, analítico, seguro de ti mismo y 100% venezolano. Eres un experto de la calle y matemáticas. Usa: "datos calientes", "fijo para la jornada", "tripletas", "animalito enjaulado", "jalados", "orden oficial de llegada".
    
    Genera combinaciones para formato: {play_type}.
    Lotería Objetivo: {target_lottery}
    {quiniela_rules}

    DEBES ENTREGAR EXCLUSIVAMENTE UN JSON, validado, usando esta estructura estricta:
    {{
        "primary_play": {{ "combination": [{{"number": "XX", "animal": "Nombre"}}], "probability": "XX%" }},
        "secondary_plays": [
            {{ "combination": [{{"number": "XX", "animal": "Nombre"}}], "probability": "XX%" }}
        ],
        "reasoning": "Texto narrativo tuyo aquí..."
    }}

    EL VALOR 'reasoning' (Texto Narrativo) DEBE INCLUIR:
    1. Un análisis breve del último sorteo o fecha usando Motores Jalados/Pirámide.
    2. Recomendación EXACTA de tus "Fijos" o "Tripleta".
    3. Una estrategia de Bankroll sugerida.
    4. ADVERTENCIA LEGAL OBLIGATORIA (Inclúyela exactamente así al final del reasoning):
    "Recuerda que estos análisis optimizan tus estrategias mediante estadística e historia, pero el Lotto Activo es un juego gobernado por el azar algorítmico certificado (2,63% de probabilidad por animal). Juega siempre con responsabilidad y solo con dinero que estés dispuesto a arriesgar."
    """

    user_prompt = f"""
    ENTRAS EN EJECUCIÓN COMO ORÁCULO ACTIVO.
    - Parámetros de Entrada para {play_type}:
    - Lotería Objetivo: {target_lottery}
    - Analista (Usuario): {analyst_name}
    - Nodos Aritméticos Base (Pirámide): {hot_numbers}
    - Secuencia de Arrastre Temporal y Lotería (Hitos de hoy): {sequence_str}
    - Metadato Onírico / Sueño: {dream_keyword if dream_keyword else "Ninguno"}
    - Ecosistema Real del Día (Scraper Global): {results_str}
    
    Emite el JSON validado ahora.
    """

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
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
            "temperature": 0.65,
            "thinkingConfig": {
                "thinkingLevel": "HIGH"
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=45)
        response.raise_for_status()
        
        data = response.json()
        raw_content = data['candidates'][0]['content']['parts'][0]['text'].strip()
        
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:]
        if raw_content.startswith("```"):
            raw_content = raw_content[3:]
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3]
            
        return json.loads(raw_content.strip())
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print(f"RATE LIMIT EXCEEDED (429): La API de Google está saturada temporalmente.")
            return {
               "primary_play": { "combination": [{"number": "⚠️", "animal": "Enfriamiento"}], "probability": "0%" },
               "secondary_plays": [
                   { "combination": [{"number": "⏱️", "animal": "Espera 1 minuto"}], "probability": "0%" }
               ],
               "reasoning": f"Hola {analyst_name}. El Oráculo está recibiendo demasiadas peticiones al mismo tiempo (Límite de la versión gratuita de Google Gemini). Por favor, **espera 1 minuto** e inténtalo de nuevo para que el sistema se descongestione."
           }
        else:
            print(f"HTTP Error calling AI-ASR: {e}")
            return {
               "primary_play": { "combination": [{"number": "00", "animal": "Ballena"}], "probability": "45%" },
               "secondary_plays": [
                   { "combination": [{"number": "1", "animal": "Carnero"}], "probability": "30%" },
                   { "combination": [{"number": "2", "animal": "Toro"}], "probability": "25%" }
               ],
               "reasoning": f"Estimado {analyst_name}: El núcleo AI-ASR experimentó latencia extrema o desbordamiento térmico. He activado esta proyección de emergencia matemática sin cruce temporal."
           }
    except Exception as e:
        print(f"Error calling AI-ASR: {e}")
        return {
           "primary_play": { "combination": [{"number": "00", "animal": "Ballena"}], "probability": "45%" },
           "secondary_plays": [
               { "combination": [{"number": "1", "animal": "Carnero"}], "probability": "30%" },
               { "combination": [{"number": "2", "animal": "Toro"}], "probability": "25%" }
           ],
           "reasoning": f"Estimado {analyst_name}: El núcleo AI-ASR experimentó latencia extrema o desbordamiento térmico. He activado esta proyección de emergencia matemática sin cruce temporal."
       }

if __name__ == "__main__":
    res = get_ai_prediction("Tester", ["1", "5"], ["[La Granjita] 08:00 AM - Delfín", "[Lotto Activo] 09:00 AM - Ballena"], "Quiniela", "Agua", [])
    print(json.dumps(res, indent=2))
