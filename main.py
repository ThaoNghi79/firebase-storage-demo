import mimetypes
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response

app = FastAPI(title="Firebase Storage Integration API")

AUTH_EMULATOR = "http://127.0.0.1:9099"
STORAGE_EMULATOR = "http://127.0.0.1:9199"
BUCKET = "default.appspot.com" # Để tên hiển thị trên trang emulator

ACCOUNTS = {
    "student": {"email": "sv1@student.tdtu.edu.vn", "password": "123456"},
    "teacher": {"email": "gv1@tdtu.edu.vn", "password": "123456"},
    "outsider": {"email": "test@gmail.com", "password": "123456"},
}


def login_as(role: str) -> str:
    """Backend tự đăng nhập thay cho account ứng với role được chọn, trả về idToken."""
    if role not in ACCOUNTS:
        raise HTTPException(status_code=400, detail=f"role phải là 1 trong: {list(ACCOUNTS.keys())}")

    acc = ACCOUNTS[role]
    res = requests.post(
        f"{AUTH_EMULATOR}/identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=fake-api-key",
        json={"email": acc["email"], "password": acc["password"], "returnSecureToken": True},
    )
    id_token = res.json().get("idToken")
    if not id_token:
        raise HTTPException(status_code=401, detail=f"Đăng nhập thất bại cho role '{role}': {res.json()}")
    return id_token


@app.put("/files")
async def upload_file(file: UploadFile = File(...), role: str = "student"):
    id_token = login_as(role)
    filename = file.filename         
    file_bytes = await file.read()

    res = requests.post(
        f"{STORAGE_EMULATOR}/v0/b/{BUCKET}/o?name=files/{filename}",
        headers={
            "Authorization": f"Firebase {id_token}",
            "Content-Type": "application/octet-stream",
        },
        data=file_bytes,
    )

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.text)

    return {"message": "Upload thành công qua backend", "role": role, "filename": filename, "firebase_response": res.json()}


@app.get("/files/{filename}")
async def download_file(filename: str, role: str = "student"):
    id_token = login_as(role)

    res = requests.get(
        f"{STORAGE_EMULATOR}/v0/b/{BUCKET}/o/files%2F{filename}?alt=media",
        headers={"Authorization": f"Firebase {id_token}"},
    )

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.text)

    content_type, _ = mimetypes.guess_type(filename)
    if not content_type:
        content_type = "application/octet-stream"

    return Response(
        content=res.content,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/files/{filename}/url")
async def get_download_url(filename: str, role: str = "student"):
    """Trả về Download URL thật (kèm token) thay vì file thô — đúng khái niệm Download URLs."""
    id_token = login_as(role)

    meta_res = requests.get(
        f"{STORAGE_EMULATOR}/v0/b/{BUCKET}/o/files%2F{filename}",
        headers={"Authorization": f"Firebase {id_token}"},
    )

    if meta_res.status_code != 200:
        raise HTTPException(status_code=meta_res.status_code, detail=meta_res.text)

    token = meta_res.json().get("downloadTokens")
    download_url = f"{STORAGE_EMULATOR}/v0/b/{BUCKET}/o/files%2F{filename}?alt=media&token={token}"

    return {"filename": filename, "role": role, "download_url": download_url}


@app.get("/")
async def root():
    return {"message": "Firebase Storage Integration API đang chạy. Xem /docs để test trực tiếp trên trình duyệt."}