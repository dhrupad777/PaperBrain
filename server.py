from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil, uuid, json
from pathlib import Path

from pipeline.run_pipeline import run_on_invoice

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TMP_DIR = Path("storage/uploads")
TMP_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/analyze")
async def analyze_invoice(file: UploadFile = File(...)):
    # save upload
    file_id = str(uuid.uuid4())
    png_path = TMP_DIR / f"{file_id}.png"

    with png_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # for prototype, we also need JSON if anomaly uses GT
    # if not present, anomaly will be skipped in pipeline (you already coded that)
    json_path = None  

    result = run_on_invoice(json_path, png_path)

    # store result
    out_path = TMP_DIR / f"{file_id}.result.json"
    out_path.write_text(json.dumps(result), encoding="utf-8")

    return {"id": file_id, "result": result}
