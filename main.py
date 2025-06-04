from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import boto3
import io
import os

app = FastAPI()

# Configuración del cliente de Textract
textract = boto3.client(
    'textract',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="us-east-1"
)

@app.post("/extract")
async def extract_text(file: UploadFile = File(...)):
    content = await file.read()
    file_stream = io.BytesIO(content)

    ext = file.filename.lower().split(".")[-1]

    try:
        if ext == "pdf":
            response = textract.start_document_text_detection(
                DocumentLocation={'Bytes': content}
            )
            return JSONResponse(
                status_code=400,
                content={"error": "Textract StartDocumentTextDetection requiere S3 para PDFs"}
            )
        elif ext in ["jpg", "jpeg", "png"]:
            response = textract.detect_document_text(
                Document={'Bytes': content}
            )
            blocks = response.get("Blocks", [])
            extracted_text = " ".join([b["Text"] for b in blocks if b["BlockType"] == "LINE"])
            return {"text": extracted_text}
        else:
            return JSONResponse(status_code=400, content={"error": "Formato no soportado"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
