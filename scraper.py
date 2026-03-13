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
        response = requests.get(url, headers=headers, timeout=10)
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

if __name__ == "__main__":
    print(json.dumps(get_today_results(), indent=2))
