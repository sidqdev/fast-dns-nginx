import os
import yaml
import jinja2
from dataclasses import dataclass


@dataclass
class DsnRecord:
    dns: str
    redirect_host: str
    has_cert: bool = False


with open("conf.yml", 'r') as f:
    data = yaml.safe_load(f)

with open("base_nginx.conf", 'r') as f:
    template = f.read()

records = [
    DsnRecord(
        dns=x['src'],
        redirect_host=x['dst'],
        has_cert=os.path.exists(f"/etc/letsencrypt/live/{x['src']}/fullchain.pem"),
    ) for x in data['routes']
]

nginx_conf = jinja2.Template(template).render(records=records)
with open("/etc/nginx/conf.d/nginx.conf", 'w') as f:
    f.write(nginx_conf)


