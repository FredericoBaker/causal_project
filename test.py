from scholarly import scholarly, ProxyGenerator
import json
import time

# --- CONFIGURAÇÃO ---
# Se tiver problemas de bloqueio, use um ProxyGenerator. 
# Para testes curtos, pode tentar sem, mas com cautela.
# pg = ProxyGenerator()
# pg.FreeProxies() # Ou use um serviço pago como ScraperAPI
# scholarly.use_proxy(pg)

def get_papers_citing_dataset(dataset_query, limit=50):
    print(f"Buscando o paper original para: {dataset_query}...")
    
    # 1. Encontrar o paper "semente" (o paper original do dataset)
    search_query = scholarly.search_pubs(dataset_query)
    dataset_paper = next(search_query)
    
    print(f"Paper encontrado: {dataset_paper['bib']['title']}")
    
    if 'citedby_url' not in dataset_paper:
        print("Este paper não possui registros de citações acessíveis.")
        return []

    # 2. Buscar os papers que citam este paper original
    print("Buscando papers que citam o original...")
    citations_query = scholarly.citedby(dataset_paper)
    
    extracted_data = []
    count = 0
    
    for paper in citations_query:
        if count >= limit:
            break
            
        # Extração de metadados básicos
        info = {
            "title": paper['bib'].get('title'),
            "author": paper['bib'].get('author'),
            "pub_year": paper['bib'].get('pub_year'),
            "venue": paper['bib'].get('venue'),
            "abstract": paper['bib'].get('abstract'),
            "pub_url": paper.get('pub_url'), # Link para o paper (pode cair em paywall)
            "eprint_url": paper.get('eprint_url'), # Link para versão gratuita (PDF/arXiv)
        }
        
        extracted_data.append(info)
        count += 1
        print(f"[{count}] Extraído: {info['title'][:50]}...")
        
        # Delay amigável para evitar bloqueios
        time.sleep(2) 
        
    return extracted_data

# --- EXECUÇÃO ---
datasets_seeds = ["Adult Dataset Census Income", "Credit Card Fraud Detection Kaggle"]
all_results = {}

for ds in datasets_seeds:
    results = get_papers_citing_dataset(ds, limit=20)
    all_results[ds] = results

# Salvar em JSON para processar depois com a LLM
with open('papers_metadata.json', 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=4)

print("\nBusca concluída. Metadados salvos em 'papers_metadata.json'.")