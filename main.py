import re
import pdfplumber
from typing import Optional
from datetime import date
from pathlib import Path
from pydantic import BaseModel, Field, field_validator, ValidationError

# ================= CONFIGURACIÓN =================
# RUTA DE TU CARPETA (Ajusta esto)
DIRECTORIO_ENTRADA = Path(r"C:\jfruvalc\Documentos Personales\Bienes Raices\La Paz\CFE")
# =================================================

MESES_MAP = {
    "ENE": 1, "FEB": 2, "MAR": 3, "ABR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AGO": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DIC": 12
}


class DatosRecibo(BaseModel):
    fecha_limite: date
    contrato: str = Field(..., min_length=10, max_length=20)
    periodo_texto: str = Field(..., pattern=r"^[A-Z]{3}-[A-Z]{3}$")

    @field_validator('contrato')
    def limpiar_contrato(cls, v):
        # Elimina cualquier caracter no numérico
        return "".join(filter(str.isdigit, v))

    @property
    def nombre_archivo_nuevo(self) -> str:
        # Formato: YYYY_MM_DD_CFE_NumeroDeContrato_MMM-MMM.pdf
        fecha_fmt = self.fecha_limite.strftime("%Y_%m_%d")
        return f"{fecha_fmt}_CFE_{self.contrato}_{self.periodo_texto}.pdf"


def normalizar_anio(anio_str: str) -> int:
    """Convierte '25' en 2025 y '2025' en 2025."""
    if len(anio_str) == 2:
        return int(f"20{anio_str}")
    return int(anio_str)


def extraer_datos_pdf(ruta_archivo: Path) -> Optional[DatosRecibo]:
    try:
        texto_completo = ""
        with pdfplumber.open(ruta_archivo) as pdf:
            # Leemos la primera página
            page = pdf.pages[0]
            texto_completo = page.extract_text() or ""

            # Normalizamos mayúsculas para facilitar regex
            texto_completo = texto_completo.upper()

        # --- 1. BUSCAR NÚMERO DE SERVICIO ---
        # En tus ejemplos aparece como: "NO. DE SERVICIO:441000800801" (sin espacio después de los dos puntos)
        # Regex: Busca "SERVICIO", seguido opcionalmente de dos puntos y espacios, y captura los dígitos
        match_contrato = re.search(r"NO\.?\s*DE\s*SERVICIO\s*[:\.]?\s*(\d+)", texto_completo)

        if not match_contrato:
            print(f"   [X] No se encontró 'NO. DE SERVICIO' en {ruta_archivo.name}")
            return None

        contrato_str = match_contrato.group(1)

        # --- 2. BUSCAR FECHA LÍMITE ---
        # En tus ejemplos: "LÍMITE DE PAGO:29 JUN 25"
        # Regex: Busca "PAGO", dos puntos opcionales, dia, mes, año
        match_fecha = re.search(r"LÍMITE\s+DE\s+PAGO\s*[:]?\s*(\d{1,2})\s+([A-Z]{3})\s+(\d{2,4})", texto_completo)

        if not match_fecha:
            print(f"   [X] No se encontró 'LÍMITE DE PAGO' en {ruta_archivo.name}")
            return None

        dia, mes_txt, anio_txt = match_fecha.groups()
        anio_num = normalizar_anio(anio_txt)
        mes_num = MESES_MAP.get(mes_txt, 1)
        fecha_obj = date(anio_num, mes_num, int(dia))

        # --- 3. BUSCAR PERIODO FACTURADO ---
        # En tus ejemplos: "PERIODO FACTURADO:10 ABR 25-11 JUN 25"
        # Necesitamos capturar el PRIMER mes (ABR) y el SEGUNDO mes (JUN)
        # Regex compleja explicada:
        #  PERIODO FACTURADO  -> Texto ancla
        #  \s*[:]?\s*         -> Dos puntos y espacios opcionales
        #  \d{1,2}            -> Día inicio (ignorado)
        #  \s+([A-Z]{3})      -> GRUPO 1: Mes Inicio (ej. ABR)
        #  .*?                -> Cualquier cosa en medio (año inicio, guion, dia fin)
        #  \d{1,2}\s+([A-Z]{3}) -> Día fin y GRUPO 2: Mes Fin (ej. JUN)
        match_periodo = re.search(r"PERIODO\s+FACTURADO\s*[:]?\s*\d{1,2}\s+([A-Z]{3}).*?-\s*\d{1,2}\s+([A-Z]{3})",
                                  texto_completo)

        periodo_str = "UNK-UNK"  # Valor por defecto
        if match_periodo:
            mes_ini = match_periodo.group(1)
            mes_fin = match_periodo.group(2)
            periodo_str = f"{mes_ini}-{mes_fin}"
        else:
            print(f"   [!] Advertencia: No se detectó el periodo correctamente en {ruta_archivo.name}")

        # Validar y retornar con Pydantic
        return DatosRecibo(
            fecha_limite=fecha_obj,
            contrato=contrato_str,
            periodo_texto=periodo_str
        )

    except Exception as e:
        print(f"   [Error Técnico] {ruta_archivo.name}: {str(e)}")
        return None


def procesar_directorio():
    if not DIRECTORIO_ENTRADA.exists():
        print(f"❌ El directorio no existe: {DIRECTORIO_ENTRADA}")
        return

    archivos = list(DIRECTORIO_ENTRADA.glob("*.pdf"))
    if not archivos:
        print("⚠️ No hay PDFs en la carpeta.")
        return

    print(f"📂 Analizando {len(archivos)} archivos en: {DIRECTORIO_ENTRADA}")

    renombrados = 0
    for archivo in archivos:
        # Si ya empieza con "text20", asumimos que ya está procesado
        if archivo.name.startswith("text20"):
            continue

        datos = extraer_datos_pdf(archivo)

        if datos:
            nuevo_nombre = datos.nombre_archivo_nuevo
            nueva_ruta = DIRECTORIO_ENTRADA / nuevo_nombre

            if nueva_ruta.exists():
                # Si es el mismo archivo, no hacemos nada
                if nueva_ruta == archivo:
                    continue
                print(f"   ⚠️ El destino ya existe: {nuevo_nombre}")
                continue

            try:
                archivo.rename(nueva_ruta)
                print(f"✅ {archivo.name} -> {nuevo_nombre}")
                renombrados += 1
            except OSError as e:
                print(f"❌ Error renombrando {archivo.name}: {e}")

    print(f"\n✨ Proceso terminado. Archivos renombrados: {renombrados}")


if __name__ == "__main__":
    procesar_directorio()