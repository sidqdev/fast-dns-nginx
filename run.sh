#!/usr/bin/env bash

set -eu

RENEW_INTERVAL_SECONDS="${RENEW_INTERVAL_SECONDS:-43200}"

log() {
    printf '[%s] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*"
}

reload_nginx() {
    attempt=1

    while [ "${attempt}" -le 10 ]; do
        master_pid="$(ps -eo pid=,comm= | awk '$2 == "nginx" { print $1; exit }')"

        if [ -n "${master_pid}" ]; then
            kill -HUP "${master_pid}"
            log "reloaded nginx (pid ${master_pid})"
            return 0
        fi

        log "nginx master process not found; retrying reload (${attempt}/10)"
        attempt=$((attempt + 1))
        sleep 3
    done

    log "nginx master process not found; skipping reload"
    return 1
}

sync_certificates() {
    log "requesting new certificates and renewing existing ones"
    python3 generate_certs.py

    log "regenerating nginx configuration"
    python3 generate_nginx_conf.py

    reload_nginx || true
}

log "starting certbot renewal loop"
sync_certificates

while true; do
    log "sleeping for ${RENEW_INTERVAL_SECONDS} seconds before next renewal check"
    sleep "${RENEW_INTERVAL_SECONDS}"
    sync_certificates
done
