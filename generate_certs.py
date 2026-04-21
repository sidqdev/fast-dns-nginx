import yaml
import subprocess
from dataclasses import dataclass
from pathlib import Path


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
        has_cert=Path(f"/etc/letsencrypt/live/{x['src']}/fullchain.pem").exists(),
    ) for x in data['routes']
]

subprocess.run(
    ["certbot", "renew", "--webroot", "-w", "/var/www/certbot", "--quiet"],
    check=True,
)

for record in records:
    if record.has_cert:
        continue
    subprocess.run(
        [
            "certbot",
            "certonly",
            "--webroot",
            "-w",
            "/var/www/certbot",
            "--non-interactive",
            "--agree-tos",
            "--email",
            data["email"],
            "-d",
            record.dns,
        ],
        check=True,
    )
