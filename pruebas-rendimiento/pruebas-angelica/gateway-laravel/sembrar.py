"""Crea, a través del API Gateway, los datos que usan las pruebas de rendimiento:
1 categoría, 100 productos (CARGA-001 ... CARGA-100) con inventario y 5 proveedores.
Se puede correr varias veces: lo que ya existe se reutiliza.

    pip install requests
    python sembrar.py
"""
import os
import random
import sys

import requests

G = os.getenv("GATEWAY_URL", "http://localhost:8000/api").rstrip("/")
H = {"Accept": "application/json"}
random.seed(7)


def filas(cuerpo):
    if isinstance(cuerpo, list):
        return cuerpo
    datos = cuerpo.get("data", [])
    return datos.get("data", []) if isinstance(datos, dict) else datos


def main():
    try:
        requests.get(f"{G}/categories", headers=H, timeout=5).raise_for_status()
    except Exception as e:  # noqa: BLE001
        sys.exit(f"El gateway no responde en {G} ({e}). Levanta primero: docker compose up -d")

    # Categoría
    cats = filas(requests.get(f"{G}/categories", headers=H).json())
    cat = next((c for c in cats if c["name"] == "Pruebas de carga"), None)
    if not cat:
        cat = requests.post(f"{G}/categories", headers=H, json={"name": "Pruebas de carga"}).json()
    print("categoría", cat["id"])

    # Productos + inventario
    existentes = {p["code"]: p["id"] for p in filas(requests.get(f"{G}/products?q=CARGA-&per_page=100", headers=H).json())}
    nombres = ["Cuaderno", "Lapiz", "Regla", "Marcador", "Borrador", "Carpeta", "Resma", "Tijeras", "Pegante", "Esfero"]
    creados = 0
    for i in range(1, 101):
        codigo = f"CARGA-{i:03d}"
        if codigo not in existentes:
            r = requests.post(f"{G}/products", headers=H, json={
                "code": codigo, "name": f"{random.choice(nombres)} {i}", "category_id": cat["id"],
                "unit": "und", "price": random.randint(500, 20000)})
            r.raise_for_status()
            existentes[codigo] = r.json()["id"]
            creados += 1
        # 1000 unidades; mínimo alto en 1 de cada 5 para que haya productos con stock bajo
        minimo = 1500 if i % 5 == 0 else 50
        r = requests.post(f"{G}/inventory", headers=H, json={
            "product_id": existentes[codigo], "quantity": 1000, "minimum_stock": minimo})
        if r.status_code not in (200, 201, 422):  # 422 = ya estaba en inventario
            r.raise_for_status()
    print(f"productos: {len(existentes)} ({creados} nuevos), con inventario")

    # Proveedores
    provs = filas(requests.get(f"{G}/suppliers?per_page=100", headers=H).json())
    for i in range(len(provs) + 1, 6):
        requests.post(f"{G}/suppliers", headers=H, json={
            "name": f"Proveedor carga {i}", "tax_id": f"900000{i:03d}-1"}).raise_for_status()
    print("proveedores:", max(len(provs), 5))
    print("Listo. Ahora:  python ejecutar.py")


if __name__ == "__main__":
    main()
