# Trusty 임시 프론트 UI

회의 설명용으로 만든 순수 HTML/CSS/JS 임시 프론트입니다.

## 실행 방법

1. FastAPI 백엔드 실행

```bash
python -m uvicorn app.main:app --reload
```

2. 이 폴더의 `index.html`을 브라우저로 열기

## 연결된 API

- POST `/auth/signup`
- POST `/auth/login`
- GET `/users/me`

## 백엔드 CORS 설정 필요

프론트에서 API 호출이 막히면 FastAPI `main.py`에 아래 설정을 추가하세요.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
##7/13 이후 돌려볼때 프로젝트 파일에서 pip install python-multipart 실행 후 진행하세요.