import requests
import re
import schedule
import time
import logging
from github import Github, UnknownObjectException

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])

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
    'https://gtmsport.tv/live-tv/sport-tv-3-38.html'
    # Adicione mais URLs conforme necessário
]

# Configuração do GitHub
github_token = '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'
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
                logging.info(f"URL m3u8 encontrada na página {page_url}: {m3u8_url}")
                m3u8_urls.append(m3u8_url)
            else:
                logging.warning(f"URL m3u8 não encontrada na página {page_url}.")
        
        except requests.RequestException as e:
            logging.error(f"Erro ao fazer a solicitação HTTP para {page_url}: {e}")
        except Exception as e:
            logging.error(f"Erro inesperado na página {page_url}: {e}")
    
    return m3u8_urls

# Função para carregar a lista IPTV existente do GitHub
def load_iptv_list_from_github(file_path):
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        file = repo.get_contents(file_path)
        return file.decoded_content.decode('utf-8').splitlines()
    except UnknownObjectException:
        logging.warning(f"Arquivo IPTV não encontrado no repositório {repo_name}. Criando um novo arquivo.")
        create_blank_file_in_github(file_path)
        return []
    except Exception as e:
        logging.error(f"Erro ao carregar o arquivo IPTV do GitHub: {e}")
        return []

# Função para criar um arquivo em branco no GitHub se não existir
def create_blank_file_in_github(file_path):
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        repo.create_file(file_path, "Criando arquivo inicial", "")
        logging.info(f"Arquivo IPTV criado com sucesso no repositório {repo_name}.")
    except Exception as e:
        logging.error(f"Erro ao criar o arquivo no repositório GitHub: {e}")

# Função para salvar a lista IPTV atualizada no GitHub
def save_iptv_list_to_github(file_path, lines):
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        current_content = '\n'.join(lines)
        repo.update_file(file_path, "Atualização automática de IPTV", current_content, repo.get_contents(file_path).sha)
        logging.info(f"Arquivo IPTV atualizado com sucesso no repositório {repo_name}.")
    except Exception as e:
        logging.error(f"Erro ao atualizar o arquivo no repositório GitHub: {e}")

# Função para atualizar a lista IPTV com novas URLs m3u8
def update_iptv_list():
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
                logging.info(f"Atualizando URL m3u8 na ordem: {updated_lines[-1]}")
        else:
            updated_lines.append(line)
    
    # Salvar a lista IPTV atualizada no GitHub
    save_iptv_list_to_github(file_path, updated_lines)

# Executar a varredura imediatamente
update_iptv_list()

# Agendar a execução da função em intervalos regulares (ex. a cada 10 minutos)
schedule.every(10).minutes.do(update_iptv_list)

# Loop para manter o script em execução
while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Script interrompido pelo usuário.")
        break
    except Exception as e:
        logging.error(f"Erro no loop principal: {e}")
        time.sleep(5)  # Espera 5 segundos antes de continuar o loop
