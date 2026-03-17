from fastapi import FastAPI

app = FastAPI(
    title="Lectica",
    description="Turn any lecture into a study companion",
    version="1.0.0",
)

@app.get("/health")
async def health():
    return {"status": "ok"}
