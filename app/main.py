from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def main() -> dict[str, str]:
    return {"hello": "fastapi"}
