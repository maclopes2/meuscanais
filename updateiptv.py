# script.py

import requests
import re
import os
from github import Github

# Lista de URLs das páginas que contêm as URLs m3u8
page_urls = [
    'https://gtmsport.tv/live-tv/tnt-sport-1-21.html',
    'https://gtmsport.tv/live-tv/tnt-sport-2-20.html',
    'https://gtmsport.tv/live-tv/tnt-sport-3-19.html',
    'https://gtmsport.tv/live-tv/tnt-sport-4-137.html',
    'https://gtmsport.tv/live-tv/premier-sports-1-26.html',
    'https://gtmsport.tv/live-tv/premier-sports-2-27.html',
    'https://gtmsport.tv/live-tv/sky-sports-football-57.html',
    'https://gtmsport.tv/live-tv/sky-sports-premier-league-58.html',
    'https://gtmsport.tv/live-tv/sky-sports-main-event-60.html',
    'https://gtmsport.tv/live-tv/sky-sports-f1-28.html',
    'https://gtmsport.tv/live-tv/fs1-86.html',
    'https://gtmsport.tv/live-tv/fs2-87.html',
    'https://gtmsport.tv/live-tv/nfl-network-91.html',
    'https://gtmsport.tv/live-tv/cbs-sports-network-70.html',
    'https://gtmsport.tv/live-tv/nba-tv-43.html',
    'https://gtmsport.tv/live-tv/bein-sports-1-40.html',
    'https://gtmsport.tv/live-tv/bein-sports-2-41.html',
    'https://gtmsport.tv/live-tv/rmc-sport-1-13.html',
    'https://gtmsport.tv/live-tv/rmc-sport-2-14.html',
    'https://gtmsport.tv/live-tv/eleven-sport-1-33.html',
    'https://gtmsport.tv/live-tv/eleven-sport-2-32.html',
    'https://gtmsport.tv/live-tv/eleven-sport-3-31.html',
    'https://gtmsport.tv/live-tv/sport-tv-1-36.html',
    'https://gtmsport.tv/live-tv/sport-tv-2-37.html',
    'https://gtmsport.tv/live-tv/sport-tv-3-38.html',
    # Adicione mais URLs conforme necessário
]

# Configuração do GitHub
github_token = os.getenv('GITHUB_TOKEN')
repo_name = 'maclopes2/meuscanais'  # Formato: usuário/repositório
file_path = 'teste'  # Caminho completo para o arquivo no repositório

# Função para extrair a URL m3u8 do código fonte de uma página
def fetch_m3u8_urls():
    m3u8_urls = []
    for page_url in page_urls:
        try:
            response = requests.get(page_url)
            response.raise_for_status()  # Gera uma exceção para status de erro HTTP
            
            # Usar regex para encontrar a primeira URL m3u8 no código fonte da página
            found_url = re.search(r'(https?://[^\s]+\.m3u8)', response.text)
            
            if found_url:
                m3u8_url = found_url.group(1)
                print(f"URL m3u8 encontrada na página {page_url}: {m3u8_url}")
                m3u8_urls.append(m3u8_url)
            else:
                print(f"URL m3u8 não encontrada na página {page_url}.")
        
        except requests.RequestException as e:
            print(f"Erro ao fazer a solicitação HTTP para {page_url}: {e}")
        except Exception as e:
            print(f"Erro inesperado na página {page_url}: {e}")
    
    return m3u8_urls

# Função para carregar a lista IPTV existente do GitHub
def load_iptv_list_from_github(file_path):
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        file = repo.get_contents(file_path)
        return file.decoded_content.decode('utf-8').splitlines()
    except Exception as e:
        print(f"Erro ao carregar o arquivo IPTV do GitHub: {e}")
        return []

# Função para salvar a lista IPTV atualizada no GitHub
def save_iptv_list_to_github(file_path, lines):
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        current_content = '\n'.join(lines)
        repo.update_file(file_path, "Atualização automática de IPTV", current_content, repo.get_contents(file_path).sha)
        print(f"Arquivo IPTV atualizado com sucesso no repositório {repo_name}.")
    except Exception as e:
        print(f"Erro ao atualizar o arquivo no repositório GitHub: {e}")

# Função principal para executar o processo de atualização
def main():
    # Carregar a lista IPTV existente do GitHub
    lines = load_iptv_list_from_github(file_path)
    
    # Obter novas URLs m3u8
    m3u8_urls = fetch_m3u8_urls()
    
    # Atualizar a lista IPTV
    updated_lines = []
    for line in lines:
        if line.startswith('http'):
            if m3u8_urls:
                updated_lines.append(m3u8_urls.pop(0))  # Adicionar a primeira URL m3u8 da lista
                print(f"Atualizando URL m3u8 na ordem: {updated_lines[-1]}")
        else:
            updated_lines.append(line)
    
    # Salvar a lista IPTV atualizada no GitHub
    save_iptv_list_to_github(file_path, updated_lines)

if __name__ == "__main__":
    main()
