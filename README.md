# Vintage House Reborn

FastAPI 기반 쇼핑몰 백엔드 API 서버

## 기술 스택

- **Framework**: FastAPI (Python 3.13)
- **Database**: PostgreSQL
- **Cache**: Redis
- **ORM**: SQLAlchemy (async) + Alembic
- **결제**: 토스페이먼츠
- **패키지 관리**: uv
- **Infra**: Docker, Docker Compose, AWS EC2

## 주요 기능

- 회원가입 / 로그인 (JWT 인증)
- 상품 CRUD
- 장바구니 (Redis)
- 결제 (토스페이먼츠)

## 프로젝트 구조

```
app/
├── auth/           # 회원가입, 로그인
│   ├── router.py   # 엔드포인트
│   ├── service.py  # 비즈니스 로직
│   ├── models.py   # SQLAlchemy 모델
│   └── schemas.py  # Pydantic 스키마
├── products/       # 상품 CRUD (auth와 동일 구조)
├── cart/           # 장바구니 (auth와 동일 구조)
├── payments/       # 결제 (auth와 동일 구조)
├── core/           # 공용 기술 (설정, DB 연결 등)
│   ├── config.py   # 환경변수 설정 (pydantic-settings)
│   └── database.py # SQLAlchemy async engine/session, BaseModel
└── main.py
```

## 브랜치 전략

```
main        ← 실서버 배포
  └── develop    ← 로컬 테스트
        └── feature/*  ← 기능 개발
```

## 시작하기

**환경변수 설정**

```bash
cp env/example.env env/.env
# env/.env 파일에 실제 값 입력
```

**서버 실행**

```bash
docker compose up --build
```

로컬 서버: `http://localhost:8001`

API 문서: `http://localhost:8001/docs`

## DB 마이그레이션 (Alembic)

```bash
# 모델 변경 감지 후 마이그레이션 파일 생성
docker compose exec fastapi uv run alembic revision --autogenerate -m "메시지"

# 마이그레이션 적용
docker compose exec fastapi uv run alembic upgrade head
```

## 개발 명령어

```bash
make format   # 코드 포맷 (black, ruff)
make type     # 타입 검사 (mypy)
make check    # 전체 검사 (format + type + test)
```

## CI/CD

| 워크플로우 | 트리거 | 역할 |
|-----------|--------|------|
| CI | develop, main PR | lint + test 자동 검사 + Discord 알림 |
| CD | main push | 빌드 → Docker Hub → EC2 자동 배포 + Discord 알림 |
