import json
import os
import pytz
import spacy 
import logging
import sys

from datetime import datetime, timedelta
from collections import Counter

nlp = spacy.load("en_core_web_sm")
logging.getLogger().setLevel(logging.INFO)

if sys.argv[1] is None: 
    logging.ERROR("Missing arg")
    raise IndexError
file_name = sys.argv[1]
if not os.path.exists('json_files'):
    logging.ERROR("Missing json_files folder")
    raise FileNotFoundError
if not os.path.exists('json_files/ingestion'):
    logging.ERROR("Missing ingestion folder")
    raise FileNotFoundError
with open(f'json_files/ingestion/{file_name}') as json_file:
    repo_json = json.load(json_file)

def get_license(repo):
    if repo.get("license") is None:
        return "no license"
    return repo.get("license").get("key") 

def fix_date(date: str):
    return datetime.fromisoformat(date.replace("Z","+00:00"))

def get_activity(repo, days_range=30):
    if len(repo["pulls"]) == 0:
        return 0
    tz_utc = pytz.timezone("UTC")
    initial_date = tz_utc.localize(datetime.now()) - timedelta(days=days_range)

    created_at = fix_date(repo["pulls"][0]["created_at"])
    updated_at = fix_date(repo["pulls"][0]["updated_at"])

    pr_list = [pr for pr in repo['pulls'] if created_at > initial_date 
                or updated_at > initial_date ]

    return len(pr_list)
def word_frequency_counter(word_to_find:str, phrase: str):
    if phrase is None:
        return 0
    doc = nlp(phrase)
    words = [token.text for token in doc if token.is_stop != True and token.is_punct != True]
    word_freq = Counter(words).get(word_to_find)

    return 1 if word_freq else 0

def get_security(repo):
    if len(repo["pulls"]) == 0:
        return 0
    repo_pulls= repo["pulls"]
    frequency = 0
    for pull in repo_pulls:
        if pull["state"] == "open":
            frequency += word_frequency_counter("security",pull['body'])
    return frequency

def get_updated(repo):
    if len(repo["pulls"]) == 0:
        return 0
    repo_pulls= repo["pulls"]
    frequency = 0
    for pull in repo_pulls:
        if pull["state"] == "open":
            frequency += word_frequency_counter("bump",pull['body'])
    return frequency

def get_engagement(repo, days_range=30):
    if len(repo["pulls"]) == 0:
        return 0
    tz_utc = pytz.timezone("UTC")
    initial_date = tz_utc.localize(datetime.now()) - timedelta(days=days_range)

    created_at = fix_date(repo["pulls"][0]["created_at"])
    updated_at = fix_date(repo["pulls"][0]["updated_at"])
    return len(set(pull["user"]["login"] for pull in repo["pulls"] if created_at > initial_date 
                or updated_at > initial_date ))

data_list = []
logging.info("Inicializing data processing!")
for repo in repo_json:
    data_dict = {
        "name" : repo["name"],
        "activity": get_activity(repo),
        "license": get_license(repo),
        "security" : get_security(repo),
        "updated" : get_updated(repo),
        "engagement": get_engagement(repo)
    }
    data_list.append(data_dict)

timestamp = datetime.now().isoformat()

if not os.path.exists('json_files/processing'):
    logging.info("Creating processing folder")
    os.makedirs('json_files/processing')

with open(f'json_files/processing/heimdall-process-{timestamp}.json', 'w') as outfile:
    json.dump(data_list, outfile)

logging.info(f"Process done! json_files/processing/heimdall-process-{timestamp}.json")