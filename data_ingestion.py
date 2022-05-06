import logging
import asyncio
from typing import Dict, List
import requests
import httpx
import json
import os

from datetime import datetime
from bs4 import BeautifulSoup


number_of_repos_per_page = 20

repo_max_size = 50
url = 'https://gitmostwanted.com/top/stars/solid'
oauth_key = "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"
HEADERS={"Authorization": f"token {oauth_key}"}

logging.getLogger().setLevel(logging.INFO)

def get_repos_name(url:str) -> List[Dict]:
    pagination = 1
    repo_url_list = []

    while len(repo_url_list) < repo_max_size:
      page = requests.get(f"{url}/{pagination}")
      soup = BeautifulSoup(page.text, 'html.parser')
      
      for li in soup.findAll("li"):
          if 'data-url' in li.attrs and len(repo_url_list) < repo_max_size:
              repo_url_list.append(li.attrs["data-url"])
      pagination = pagination + 1
    return repo_url_list

async def get_repos(user_repo_list:List[str], headers:Dict) -> Dict:
  repo_result=[]
  repo_list = []

  for url in user_repo_list:
    async with httpx.AsyncClient() as client:
        logging.info(f'https://api.github.com/repos/{url} - has innited')
        try:
          repo_response = await client.get(f'https://api.github.com/repos/{url}',headers=headers )
          repo_result = repo_response.json()
        
          pr_request = await client.get(repo_result["pulls_url"].replace("{/number}", ""), headers=headers)
          pr_result = pr_request.json()
          
          repo_result["pulls"] = pr_result
          
          repo_list.append(repo_result)
          logging.info(f'https://api.github.com/repos/{url} - has finished' )
        except httpx.ReadTimeout:
          logging.error("error on get repo")
          
  return repo_list

logging.info("Inicializing data ingestion!")

repo_url_list = get_repos_name(url)

user_repo_list = [item.replace('https://github.com/', '') for item in repo_url_list]

logging.info("Repos name collected!")

repo_list = asyncio.run(get_repos(user_repo_list, HEADERS))

logging.info("Repos collected!")

timestamp = datetime.now().isoformat()
if not os.path.exists('json_files'):
    logging.info("Creating json_files folder")
    os.makedirs('json_files')
if not os.path.exists('json_files/ingestion'):
    logging.info("Creating ingestion folder")
    os.makedirs('json_files/ingestion')
with open(f'json_files/ingestion/heimdall-{timestamp}.json', 'w') as outfile:
    json.dump(repo_list, outfile)
logging.info(f"File saved on json_files/ingestion/heimdall-ingestion-{timestamp}.json")