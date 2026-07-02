from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def main() -> dict[str, str]:
    return {"hello": "fastapi", "test": "이거잘 반영돼는거 맞죠?"}
