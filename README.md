# Vintage House Reborn

FastAPI 기반 쇼핑몰 백엔드 API 서버

## 기술 스택

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Cache**: Redis
- **ORM**: SQLAlchemy (async)
- **Migration**: Alembic
- **결제**: 토스페이먼츠
- **Infra**: Docker, Docker Compose

## 주요 기능

- 회원가입 / 로그인 (JWT 인증)
- 상품 CRUD
- 장바구니 (Redis)
- 결제 (토스페이먼츠)

## 프로젝트 구조

```
app/
├── auth/           # 회원가입, 로그인
├── products/       # 상품 CRUD
├── cart/           # 장바구니
├── payments/       # 결제
└── main.py
```

## 시작하기

**환경변수 설정**

```bash
cp env/example.env env/.env
# env/.env 파일 수정
```

**서버 실행**

```bash
docker compose up --build
```

서버 주소: `http://localhost:8001`

API 문서: `http://localhost:8001/docs`

## 개발 명령어

```bash
make format   # 코드 포맷 (black, ruff)
make type     # 타입 검사 (mypy)
make check    # 전체 검사 (format + type + test)
```
