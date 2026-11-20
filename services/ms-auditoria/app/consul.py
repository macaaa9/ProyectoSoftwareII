"""Registro del servicio en Consul (service discovery). El gateway resuelve 'ms-auditoria' consultando Consul."""
import logging
import time

import requests

log = logging.getLogger("consul")


def _id_servicio(cfg):
    return f"{cfg['SERVICE_NAME']}-{cfg['SERVICE_ADDRESS']}-{cfg['SERVICE_PORT']}".replace(".", "-")


def registrar(cfg, intentos=5):
    if not cfg.get("CONSUL_REGISTER"):
        log.info("registro en Consul desactivado (CONSUL_REGISTER=false)")
        return False
    direccion, puerto = cfg["SERVICE_ADDRESS"], cfg["SERVICE_PORT"]
    cuerpo = {
        "ID": _id_servicio(cfg),
        "Name": cfg["SERVICE_NAME"],
        "Address": direccion,
        "Port": puerto,
        "Tags": ["flask", "papiers"],
        "Check": {
            "HTTP": f"http://{direccion}:{puerto}/health",
            "Interval": "10s",
            "Timeout": "3s",
            "DeregisterCriticalServiceAfter": "30m",
        },
    }
    for intento in range(1, intentos + 1):
        try:
            r = requests.put(f"{cfg['CONSUL_URL']}/v1/agent/service/register", json=cuerpo, timeout=3)
            r.raise_for_status()
            log.info("registrado en Consul", extra={"campos": {"id": cuerpo["ID"], "direccion": direccion}})
            return True
        except requests.RequestException as e:
            log.warning(f"Consul no disponible (intento {intento}/{intentos}): {e}")
            time.sleep(2 * intento)
    log.error("no se pudo registrar en Consul; el servicio sigue funcionando por DNS de Kubernetes")
    return False


def desregistrar(cfg):
    if not cfg.get("CONSUL_REGISTER"):
        return
    try:
        requests.put(f"{cfg['CONSUL_URL']}/v1/agent/service/deregister/{_id_servicio(cfg)}", timeout=3)
        log.info("retirado de Consul")
    except requests.RequestException as e:
        log.warning(f"no se pudo retirar de Consul: {e}")
