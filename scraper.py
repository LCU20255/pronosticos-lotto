import requests
from bs4 import BeautifulSoup
import json
import concurrent.futures

LOTTERIES = {
    "Lotto Activo": "lottoactivo",
    "La Granjita": "lagranjita",
    "Ruleta Activa": "ruletaactiva"
}

def scrape_lottery(name, slug):
    """Scrapes a single lottery."""
    url = f"https://www.loteriadehoy.com/animalito/{slug}/resultados/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    results = []
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        result_blocks = soup.find_all("div", class_="circle-legend")
        
        for block in result_blocks:
            h4_tag = block.find('h4')
            h5_tag = block.find('h5')

            if h4_tag and h5_tag:
                animal = h4_tag.text.strip()
                schedule_full = h5_tag.text.strip()
                
                # Extract just the time part, removing any lottery brand names
                schedule = schedule_full.replace("Lotto Activo ", "").replace("La Granjita ", "").replace("Ruleta Activa ", "").strip()
                
                results.append({
                    "schedule": schedule,
                    "animal": animal
                })
    except Exception as e:
        print(f"Error scraping {name}: {e}")
        
    return name, results

def get_today_results():
    """
    Scrapes today's results for multiple lotteries concurrently.
    Returns a dict: {'Lotto Activo': [...], 'La Granjita': [...], 'Ruleta Activa': [...]}
    """
    
    final_data = {}
    
    # Run requests concurrently for speed
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(scrape_lottery, name, slug): name for name, slug in LOTTERIES.items()}
        for future in concurrent.futures.as_completed(futures):
            name, results = future.result()
            final_data[name] = results
            
    return final_data

def scrape_internet_consensus():
    """Scrapes DuckDuckGo HTML Lite for 'datos lotto activo hoy' and returns the hottest animals"""
    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"q": "datos de lotto activo hoy pronosticos animalitos"}
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        snippets = soup.find_all('a', class_='result__snippet')
        full_text = " ".join([s.text for s in snippets]).lower()
        
        animal_counts = {}
        animals_list = ["delfín", "ballena", "carnero", "toro", "ciempiés", "alacrán", "león", "rana", "perico", "ratón", "águila", "tigre", "gato", "caballo", "mono", "paloma", "zorro", "oso", "pavo", "burro", "chivo", "cochino", "gallo", "camello", "cebra", "iguana", "gallina", "vaca", "perro", "zamuro", "elefante", "caimán", "lapa", "ardilla", "pescado", "venado", "jirafa", "culebra"]
        
        for a in animals_list:
            count = full_text.count(a)
            a_no_accents = a.replace('í', 'i').replace('á', 'a').replace('é', 'e').replace('ó', 'o').replace('ú', 'u')
            if a != a_no_accents:
                count += full_text.count(a_no_accents)
            if count > 0:
                animal_counts[a] = count
                
        sorted_animals = sorted(animal_counts.items(), key=lambda item: item[1], reverse=True)
        return [f"{a.capitalize()} (Menciones: {c})" for a, c in sorted_animals[:5]]
    except Exception as e:
        print(f"Error scraping consensus: {e}")
        return []

if __name__ == "__main__":
    print(json.dumps(get_today_results(), indent=2))
