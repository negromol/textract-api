# Servicio de AWS Textract para Make

Este microservicio en FastAPI expone dos endpoints:

- `/start-textract`: Inicia el OCR de un archivo PDF o imagen desde un bucket S3.
- `/get-textract-result`: Obtiene el resultado del OCR.

## Cómo usar

1. Desplegá este código en Railway, Render o similar.
2. Usá Make (Integromat) con el módulo HTTP para conectar con estos endpoints.