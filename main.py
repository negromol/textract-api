import boto3
import uuid
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os

app = FastAPI()

# Región corregida (por defecto us-east-2)
region = os.getenv("AWS_REGION", "us-east-2")

# Inicializar clientes con la región correcta
s3_client = boto3.client("s3", region_name=region)
textract_client = boto3.client("textract", region_name=region)

BUCKET_NAME = os.getenv("BUCKET_NAME", "facturas-automatizadas-tuempresa")

@app.post("/extract")
async def extract_text(file: UploadFile = File(...)):
    contents = await file.read()
    file_key = f"uploads/{uuid.uuid4()}_{file.filename}"

    try:
        # Subida del archivo a S3
        s3_client.put_object(Bucket=BUCKET_NAME, Key=file_key, Body=contents)
        print(f"✅ Archivo subido: bucket={BUCKET_NAME}, key={file_key}")

        # Llamado a Textract
        response = textract_client.start_document_text_detection(
            DocumentLocation={"S3Object": {"Bucket": BUCKET_NAME, "Name": file_key}}
        )
        job_id = response["JobId"]
        print(f"✅ Análisis iniciado con JobId: {job_id}")
        return {"message": "Análisis iniciado", "job_id": job_id}
    except Exception as e:
        print(f"❌ ERROR al iniciar Textract: {e}")
        return JSONResponse(content={"error": f"Error iniciando Textract: {str(e)}"}, status_code=500)

@app.get("/extract/{job_id}")
def get_results(job_id: str):
    try:
        response = textract_client.get_document_text_detection(JobId=job_id)
        status = response["JobStatus"]

        if status == "SUCCEEDED":
            blocks = response.get("Blocks", [])
            text = " ".join([b["Text"] for b in blocks if b["BlockType"] == "LINE"])
            return {"text": text}
        else:
            return {"status": status}
    except Exception as e:
        return JSONResponse(content={"error": f"Error obteniendo resultados: {str(e)}"}, status_code=500)
