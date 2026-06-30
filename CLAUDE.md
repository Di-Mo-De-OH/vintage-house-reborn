# Vintage House Reborn — 프로젝트 컨텍스트

## 프로젝트 개요

FastAPI 기반 쇼핑몰 백엔드 API 서버

## 기술 스택

- Python 3.13 / FastAPI / SQLAlchemy (async) / Alembic
- PostgreSQL (메인 DB) / Redis (장바구니 캐시)
- Docker Compose로 전체 인프라 관리
- 결제: 토스페이먼츠

## 아키텍처

기능별 분리 (Feature-based)

```
app/
├── auth/        # 회원가입, 로그인 (JWT)
├── products/    # 상품 CRUD
├── cart/        # 장바구니 (Redis)
├── payments/    # 결제 (토스페이먼츠)
└── main.py
```

각 앱 내부 구조:
```
{app}/
├── router.py    # 엔드포인트
├── service.py   # 비즈니스 로직
├── models.py    # SQLAlchemy 모델
└── schemas.py   # Pydantic 스키마
```

## 포트

| 서비스 | 포트 |
|--------|------|
| FastAPI | 8001 |
| PostgreSQL | 5434 |
| Redis | 6480 |

## 환경변수

`env/.env` 파일 사용 (docker compose가 컨테이너에 주입)

## 개발 명령어

```bash
docker compose up --build    # 서버 실행
make format                  # black + ruff
make type                    # mypy
make check                   # 전체 검사
```

## 컨벤션

- 모든 함수에 타입 힌트 필수 (mypy strict)
- 비동기 엔드포인트 사용 (async def)
- 에러 응답 포맷: `{"detail": "..."}`
