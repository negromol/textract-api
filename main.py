from fastapi import FastAPI, Request
import boto3
from pydantic import BaseModel
from botocore.config import Config

app = FastAPI()

class TextractRequest(BaseModel):
    accessKey: str
    secretKey: str
    region: str
    bucket: str
    fileName: str

@app.post("/start-textract")
def start_textract(req: TextractRequest):
    session = boto3.Session(
        aws_access_key_id=req.accessKey,
        aws_secret_access_key=req.secretKey,
        region_name=req.region
    )
    textract = session.client("textract", config=Config(region_name=req.region))

    response = textract.start_document_text_detection(
        DocumentLocation={"S3Object": {"Bucket": req.bucket, "Name": req.fileName}}
    )
    return {"JobId": response["JobId"]}


@app.post("/get-textract-result")
def get_textract_result(req: TextractRequest, jobId: str):
    session = boto3.Session(
        aws_access_key_id=req.accessKey,
        aws_secret_access_key=req.secretKey,
        region_name=req.region
    )
    textract = session.client("textract", config=Config(region_name=req.region))

    response = textract.get_document_text_detection(JobId=jobId)
    blocks = response.get("Blocks", [])
    text = " ".join([block["Text"] for block in blocks if block["BlockType"] == "LINE"])
    return {"Text": text}