import yaml
import databases

with open('config.yml', 'r', encoding='utf-8') as f:
    config = yaml.full_load(f)

config_db = config.get('db', {}).get('mysql', {})
user = config_db.get('user', 'root')
password = config_db.get('password', '')
host = config_db.get('host', 'localhost')
port = config_db.get('port', 3306)
database_ = config_db['database']

DATABASE_URL = f'mysql://{user}{f":{password}" if password else ""}@{host}{f":{port}" if port else ""}/{database_}'

database = databases.Database(DATABASE_URL)