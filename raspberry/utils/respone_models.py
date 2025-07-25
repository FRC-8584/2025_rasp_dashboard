from fastapi.responses import JSONResponse

def success_response(data: dict = {}) -> JSONResponse:
    return JSONResponse(content={"error": False, **data})

def error_response(message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": True, "message": message}
    )