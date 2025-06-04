
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import boto3
import logging
from botocore.exceptions import BotoCoreError, ClientError

app = FastAPI()

# Configurar logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("textract-api")

@app.post("/extract")
async def extract_text(file: UploadFile = File(...)):
    logger.info("📥 Archivo recibido: %s", file.filename)
    try:
        contents = await file.read()
        logger.info("📦 Tamaño del archivo: %d bytes", len(contents))

        # Cliente Textract
        client = boto3.client("textract", region_name="us-east-1")

        # Llamar a Textract
        logger.info("🚀 Enviando archivo a AWS Textract...")
        response = client.analyze_document(
            Document={"Bytes": contents},
            FeatureTypes=["TABLES", "FORMS"]
        )

        logger.info("✅ Respuesta de AWS recibida correctamente")
        return response

    except (BotoCoreError, ClientError) as aws_error:
        logger.error("❌ Error en AWS Textract: %s", str(aws_error))
        return JSONResponse(status_code=500, content={"error": "AWS Textract error"})

    except Exception as e:
        logger.error("❌ Error general en /extract: %s", str(e))
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
