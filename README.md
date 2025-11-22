# CFE PDF Organizer

## Descripción
**CFE PDF Organizer** es una herramienta profesional diseñada para automatizar la organización de recibos de la Comisión Federal de Electricidad (CFE). Utilizando técnicas avanzadas de extracción de datos, este script analiza archivos PDF, extrae información crítica como la fecha límite de pago, el número de contrato y el periodo de facturación, y renombra los archivos para un archivado estructurado y eficiente.

## Tecnologías Utilizadas
Este proyecto está construido con un stack moderno de Python:
- **[uv](https://github.com/astral-sh/uv)**: Para una gestión de dependencias y entornos virtuales ultrarrápida.
- **[pdfplumber](https://github.com/jsvine/pdfplumber)**: Para una extracción precisa de texto de los archivos PDF.
- **[pydantic](https://docs.pydantic.dev/)**: Para la validación robusta de datos y modelado de la información extraída.

## Instalación
Asegúrate de tener `uv` instalado en tu sistema. Luego, sincroniza el entorno del proyecto:

```bash
uv sync
```

## Uso
Para ejecutar el organizador, utiliza el siguiente comando:

```bash
uv run main.py
```

El script buscará archivos PDF en el directorio configurado, extraerá los datos necesarios y los renombrará automáticamente.

## Configuración
Antes de ejecutar, verifica la variable `DIRECTORIO_ENTRADA` en el archivo `main.py` para asegurarte de que apunte a la carpeta donde se encuentran tus recibos de CFE.

```python
# main.py
DIRECTORIO_ENTRADA = Path(r"C:\Ruta\A\Tus\Recibos")
```

## Lógica de Renombrado
Los archivos se renombran siguiendo un formato estandarizado que facilita el ordenamiento cronológico y la identificación rápida:

**Formato:** `YYYY_MM_DD_CFE_Contrato_Periodo.pdf`

- **YYYY_MM_DD**: Fecha límite de pago (para ordenamiento cronológico).
- **Contrato**: Número de servicio/contrato extraído.
- **Periodo**: Periodo facturado (ej. `ENE-MAR`).

**Ejemplo:**
`2025_06_29_CFE_441000800801_ABR-JUN.pdf`
