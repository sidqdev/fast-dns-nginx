import os
import yaml
from dataclasses import dataclass


@dataclass
class DsnRecord:
    dns: str
    redirect_host: str
    has_cert: bool = False


with open("conf.yml", 'r') as f:
    data = yaml.safe_load(f)

records = [
    DsnRecord(
        dns=x['src'],
        redirect_host=x['dst'],
        has_cert=os.path.exists(f"/etc/letsencrypt/live/{x['src']}/fullchain.pem;"),
    ) for x in data['routes']
]

os.system("certbot renew --webroot -w /var/www/certbot --quiet")

for record in records:
    if record.has_cert:
        continue 
    os.system(f"certbot certonly --webroot -w /var/www/certbot --non-interactive --agree-tos --email {data['email']} -d {record.dns}")
