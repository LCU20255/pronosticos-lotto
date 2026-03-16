import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import random
import scraper
import ai_service

# Define absolute paths for templates and static files to ensure production compatibility
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

print(f"--- RENDER DEBUG ---")
print(f"Base Dir: {base_dir}")
print(f"Template Dir: {template_dir} (Exists: {os.path.exists(template_dir)})")
if os.path.exists(template_dir):
    print(f"Files in templates: {os.listdir(template_dir)}")
print(f"Static Dir: {static_dir} (Exists: {os.path.exists(static_dir)})")
print(f"--------------------")

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Basic dictionary of animals mapping for Lotto Activo
ANIMALS = {
    "0": "Delfín", "00": "Ballena", "1": "Carnero", "2": "Toro",
    "3": "Ciempiés", "4": "Alacrán", "5": "León", "6": "Rana",
    "7": "Perico", "8": "Ratón", "9": "Águila", "10": "Tigre",
    "11": "Gato", "12": "Caballo", "13": "Mono", "14": "Paloma",
    "15": "Zorro", "16": "Oso", "17": "Pavo", "18": "Burro",
    "19": "Chivo", "20": "Cochino", "21": "Gallo", "22": "Camello",
    "23": "Cebra", "24": "Iguana", "25": "Gallina", "26": "Vaca",
    "27": "Perro", "28": "Zamuro", "29": "Elefante", "30": "Caimán",
    "31": "Lapa", "32": "Ardilla", "33": "Pescado", "34": "Venado",
    "35": "Jirafa", "36": "Culebra"
}

# Invert dictionary for dream lookup, mapping lower case of the animal name to the number
# Also padding 1-9 with a leading zero if needed, but the prompt says Águila (09) so let's enforce 2 digits for 1-9
DREAMS_DICT = {
    v.lower(): f"0{k}" if len(str(k)) == 1 and k != "0" else k 
    for k, v in ANIMALS.items()
}

# Ensure 00 remains 00
DREAMS_DICT["ballena"] = "00"

# Specific pulls mapping provided in the prompt, extended for all 38 animals algorithmically
PULLS_DICT = {
    "0": ["Oso", "Pescado", "Ballena"],
    "00": ["Delfín", "Caimán", "Iguana", "Pescado", "Perro"],
    "5": ["Tigre", "Gato", "Elefante", "Caballo", "Gallo", "Perico"],
    "10": ["Cebra", "Ardilla", "Carnero", "Chivo", "Venado", "Mono", "Elefante"],
    "25": ["Gallo", "Toro", "Ciempiés", "Iguana", "Alacrán", "Perro"],
    "33": ["Delfín", "Ballena", "Oso", "Burro", "Perico", "Mono", "Ratón"],
    "36": ["Iguana", "Chivo", "Ratón", "Zorro", "Pescado"]
}

# Complete the rest of the 38 animals algorithmically to avoid empty pulls
keys_list = list(ANIMALS.keys())
for i, k in enumerate(keys_list):
    if k not in PULLS_DICT:
        # Pseudo-random but deterministic pulls based on indices (+3, +7, +11)
        pull1 = ANIMALS[keys_list[(i + 3) % 38]]
        pull2 = ANIMALS[keys_list[(i + 7) % 38]]
        pull3 = ANIMALS[keys_list[(i + 11) % 38]]
        PULLS_DICT[k] = [pull1, pull2, pull3]

def calculate_enjaulados(todays_results, past_animals):
    appeared = set()
    if past_animals:
        for pa in past_animals:
            parts = pa.split(' - ')
            if len(parts) == 2:
                appeared.add(parts[1].lower())
    
    if todays_results:
        for lot, results in todays_results.items():
            for r in results:
                appeared.add(r['animal'].split(' ', 1)[-1].lower())

    enjaulados = []
    for num, animal in ANIMALS.items():
        if animal.lower() not in appeared:
            enjaulados.append(f"{num} {animal}")
    
    random.seed(datetime.now().day) # simple daily deterministic shuffle
    random.shuffle(enjaulados)
    return enjaulados[:5] if len(enjaulados) > 5 else enjaulados


@app.route('/')
def index():
    return render_template('index.html', animals=ANIMALS)

@app.route('/api/pyramid', methods=['POST'])
def pyramid():
    data = request.json
    base_str = data.get('number', '')
    if not base_str.isdigit():
         return jsonify({"error": "Debe ser una cadena numérica"}), 400
    
    rows = [list(map(int, base_str))]
    
    while len(rows[-1]) > 1:
        current_row = rows[-1]
        next_row = []
        for i in range(len(current_row) - 1):
            next_row.append((current_row[i] + current_row[i+1]) % 10)
        rows.append(next_row)
    
    # Extract hot numbers: corners and tip
    hot_numbers = set()
    if len(rows) > 0:
        hot_numbers.add(rows[0][0])
        hot_numbers.add(rows[0][-1])
        if len(rows) > 1:
            hot_numbers.add(rows[-1][0])
            hot_numbers.add(rows[-1][-1]) # also add the other tip elements if they exist, or just the single tip node if 1 element
    
    return jsonify({
        "pyramid": rows,
        "hot_numbers": list(hot_numbers)
    })

@app.route('/api/pulls/<number>')
def pulls(number):
    if number in PULLS_DICT:
        pulls = PULLS_DICT[number]
    else:
        # Generate some random pulls if not in the basic dictionary as fallback
        pulls = [ANIMALS[str(random.choice(list(range(1, 37))))] for _ in range(3)]
        
    return jsonify({"number": number, "animal": ANIMALS.get(number), "pulls": pulls})

import re
STOP_WORDS = {"yo", "soñe", "soñé", "con", "un", "una", "el", "la", "los", "las", "que", "y", "de", "en", "mi", "me"}

@app.route('/api/dreams')
def dreams():
    keyword_phrase = request.args.get('q', '').lower()
    
    # NLP Tokenization and stopword removal
    words = re.findall(r'\b\w+\b', keyword_phrase)
    clean_words = [w for w in words if w not in STOP_WORDS]
    
    matches = []
    if not clean_words:
        clean_words = [keyword_phrase]

    for word in clean_words:
        # Stemming plural
        stemmed = word[:-1] if word.endswith('s') and len(word) > 3 else word
            
        for dream, number in DREAMS_DICT.items():
            if stemmed in dream or word in dream:
                entry = {"dream": dream.capitalize(), "number": number}
                if entry not in matches:
                    matches.append(entry)
            
    return jsonify(matches)

@app.route('/api/random')
def random_animals():
    count_str = request.args.get('count', '3')
    try:
        count = int(count_str)
    except ValueError:
        count = 3
        
    if count not in [1, 3, 5]:
        count = 3
    
    # Random selection
    keys = list(ANIMALS.keys())
    selected_keys = random.sample(keys, count)
    selected = [{"number": k, "animal": ANIMALS[k]} for k in selected_keys]
    
    return jsonify(selected)

@app.route('/api/today-results')
def today_results():
    results = scraper.get_today_results()
    return jsonify(results)

@app.route('/api/advanced-prediction', methods=['POST'])
def advanced_prediction():
    data = request.json
    analyst_name = data.get('analyst_name', 'Analista')
    hot_numbers = data.get('hot_numbers', [])
    past_animals = data.get('past_animals', [])
    play_type = data.get('play_type', 'Sencilla')
    target_lottery = data.get('target_lottery', 'Lotto Activo')
    dream = data.get('dream', '')
    
    # 1. Fetch today's context so the AI knows reality
    todays_results = scraper.get_today_results()
    
    # 2. Calculate "Enjaulados" mathematically
    enjaulados = calculate_enjaulados(todays_results, past_animals)
    
    # 3. Scrape Internet Consensus
    internet_consensus = scraper.scrape_internet_consensus()
    
    # 4. Call the AI Service
    ai_response = ai_service.get_ai_prediction(
        analyst_name=analyst_name,
        hot_numbers=hot_numbers, 
        past_animals=past_animals, 
        play_type=play_type,
        target_lottery=target_lottery,
        dream_keyword=dream, 
        todays_results=todays_results,
        enjaulados=enjaulados,
        internet_consensus=internet_consensus
    )
    
    # 3. Save to knowledge base (JSONL)
    try:
        log_dir = os.path.join(app.root_path, 'data')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "analyst_name": analyst_name,
            "play_type": play_type,
            "inputs": {
                "hot_numbers": hot_numbers,
                "past_animals": past_animals,
                "dream": dream,
                "todays_results": todays_results
            },
            "ai_output": ai_response
        }
        
        with open(os.path.join(log_dir, 'analysis_history.jsonl'), 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"Error saving analysis log: {e}")
        
    return jsonify(ai_response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
