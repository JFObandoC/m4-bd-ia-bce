"""Resume exportaciones por producto y calcula su participacion en el total.
Integrantes: no especificados en el repositorio.
Fuente: datos/exportaciones.csv, archivo de ejemplo sintetico del curso.
SI FALLA: el flujo registra el error y se detiene sin guardar el resultado; avisar al responsable de los datos del curso."""
import logging, sys
from datetime import date
import pandas as pd

# ---------- 1 · PARAMETROS (todo lo que puede cambiar, junto y arriba) ----------
RUTA_ENTRADA    = "datos/exportaciones.csv"
SALIDA          = f"salida/mi_flujo_{date.today().isoformat()}.csv"
FILAS_ESPERADAS = 7
TOTAL_ESPERADO  = 8679.13

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                    handlers=[logging.FileHandler("flujo.log"), logging.StreamHandler()])
log = logging.getLogger("mi_flujo")

# ---------- 2 · LAS TRES FUNCIONES (cada una con su docstring) ----------
def extraer():
    """Lee el archivo CSV de exportaciones y registra cuantas filas recibio."""
    tabla = pd.read_csv(RUTA_ENTRADA)
    log.info("extraidas %d filas", len(tabla))
    return tabla

def transformar(tabla):
    """Valida los datos y calcula la participacion porcentual de cada producto."""
    if len(tabla) != FILAS_ESPERADAS:
        raise ValueError(f"esperaba {FILAS_ESPERADAS} filas y llegaron {len(tabla)}")
    columnas = {"producto", "monto_mm_usd"}
    if not columnas.issubset(tabla.columns):
        faltantes = sorted(columnas - set(tabla.columns))
        raise ValueError(f"faltan columnas requeridas: {faltantes}")

    resultado = tabla.copy()
    resultado["producto"] = resultado["producto"].astype("string").str.strip()
    resultado["monto_mm_usd"] = pd.to_numeric(resultado["monto_mm_usd"], errors="raise")
    if resultado[["producto", "monto_mm_usd"]].isna().any().any():
        raise ValueError("producto y monto_mm_usd no pueden contener valores vacios")
    if resultado["producto"].eq("").any():
        raise ValueError("producto no puede estar vacio")

    total = round(resultado["monto_mm_usd"].sum(), 2)
    if abs(total - TOTAL_ESPERADO) > 0.01:
        raise ValueError(f"el total cambio: esperaba {TOTAL_ESPERADO} y salio {total}")

    resultado["participacion_pct"] = (resultado["monto_mm_usd"] / total * 100).round(2)
    log.info("transformadas %d filas; total validado: %.2f", len(resultado), total)
    return resultado

def cargar(tabla):
    """Guarda el resultado en CSV con la fecha de ejecucion en el nombre."""
    import os; os.makedirs("salida", exist_ok=True)
    tabla.to_csv(SALIDA, index=False)
    log.info("guardado %s (%d filas)", SALIDA, len(tabla))

# ---------- 3 · LA LOGICA, EN ORDEN ----------
if __name__ == "__main__":
    try:
        cargar(transformar(extraer())); log.info("FIN OK")
    except Exception as error:
        log.error("EL FLUJO FALLO: %s", error); sys.exit(1)
