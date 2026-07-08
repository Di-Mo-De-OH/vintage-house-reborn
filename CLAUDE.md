# Vintage House Reborn — Claude 컨텍스트

## 프로젝트 개요

FastAPI 기반 쇼핑몰 백엔드 API 서버 (2주 개발 목표)

## 기술 스택

- Python 3.13 / FastAPI / SQLAlchemy (async) / Alembic
- PostgreSQL (메인 DB) / Redis (장바구니 캐시)
- 결제: 토스페이먼츠
- 패키지 관리: uv
- 인프라: Docker Compose, AWS EC2

## 아키텍처

기능별 분리 (Feature-based)

```
app/
├── auth/        # 회원가입, 로그인 (JWT), 이메일 인증
├── products/    # 상품 CRUD
├── cart/        # 장바구니 (Redis, 테이블 없음)
├── payments/    # 결제 (토스페이먼츠)
├── core/        # 공용 기술 (config, database, redis, utils)
└── main.py
```

각 앱 내부 구조:
```
{app}/
├── router.py       # 엔드포인트 (라우팅 배선만, 문서/에러 정의는 responses.py로)
├── responses.py    # 엔드포인트별 OpenAPI 에러 응답 문서 (status code → 설명/예시)
├── service/        # 비즈니스 로직 (기능별로 파일 분리, 예: service/email.py)
├── models.py       # SQLAlchemy 모델
└── schemas.py      # Pydantic 스키마
```

`core/` 구조:
```
core/
├── config.py         # pydantic-settings, DATABASE_URL/REDIS_URL은 컴포넌트 조합 방식(@property)
├── database.py        # async engine/session, BaseModel(id=ULID, created_at, updated_at 공통 제공)
├── redis.py            # redis.asyncio 클라이언트
└── utils/
    ├── security.py     # OTP 코드/토큰 생성 (secrets 모듈, random 금지)
    └── validators.py   # 재사용 가능한 Pydantic 검증 타입 (Annotated + AfterValidator)
```

### 공통 원칙
- 각 앱 `models.py`는 `BaseModel` 상속 → `id`(ULID)/`created_at`/`updated_at` 자동 포함
- 부모 없이 존재 의미 없는 자식 테이블(RefreshToken, ProductImage, OrderItem, Payment 등)은 FK에 `ondelete="CASCADE"` 필수
- 새 모델 추가 시 `alembic/env.py`에 `import app.{app}.models` 추가해야 autogenerate가 인식함
- 비밀번호 등 민감정보는 **저장 위치를 하나로 통일** (예: `DATABASE_URL`을 별도 값으로 안 두고 `POSTGRES_PASSWORD` 등 컴포넌트에서 조합 — 중복 저장 시 값이 어긋나는 사고 경험함)
- URL에 비밀번호를 조합할 때는 `urllib.parse.quote()`로 이스케이프 (비밀번호에 `/`, `+` 등 특수문자 포함 시 URL 파싱이 깨짐)

## 브랜치 전략

```
main        ← 실서버 배포 (CD 트리거)
  └── develop    ← 로컬 테스트 기준
        └── feature/auth
        └── feature/products
        └── feature/cart
        └── feature/payments
```

- `feature → develop` PR: CI 실행 (lint + test)
- `develop → main` PR: CI 실행
- `main` 머지: CD 실행 (서버 자동 배포)

## 포트

| 환경 | FastAPI | PostgreSQL | Redis |
|------|---------|------------|-------|
| 로컬 | 8001 | 5434 | 6480 |
| 서버 | 8000 | 5432 | 6379 |

로컬 포트가 다른 이유: 다님(Danim) 프로젝트와 충돌 방지

## 환경변수

`env/.env` 파일 사용 (docker compose가 컨테이너에 주입). `DATABASE_URL`/`REDIS_URL`은 값을 직접 넣지 않음 — `app/core/config.py`가 아래 컴포넌트 값들로 조합해서 자동 생성함 (중복 저장 방지).

```
# Postgres
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=

# Redis
REDIS_HOST=
REDIS_PORT=
REDIS_DB=
REDIS_PASSWORD=

# JWT
SECRET_KEY=
ALGORITHM=
ACCESS_TOKEN_EXPIRE_MINUTES=
REFRESH_TOKEN_EXPIRE_DAYS=

# SMTP (네이버 메일, 이메일 인증 발송용)
SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=

# 결제 (코드 작성 후 추가 예정)
TOSS_SECRET_KEY=
TOSS_CLIENT_KEY=
```

네이버 SMTP는 2단계 인증 + 애플리케이션 비밀번호 필수 (일반 로그인 비밀번호 사용 불가, 2025-06-24부터 정책 변경). Host: `smtp.naver.com`, Port: `465`(SSL).

## Docker 구성

- `docker-compose.yml` — 로컬 개발용 (build: ., --reload)
- `docker-compose.prod.yml` — 서버 배포용 (Docker Hub 이미지, restart: always)
- EC2에서는 `docker-compose`(하이픈) v2 사용 (`/usr/local/bin/docker-compose`)

## CI/CD

**CI (`.github/workflows/ci.yml`)**
- 트리거: develop, main 브랜치 PR
- lint (black, ruff, mypy) + test (coverage + pytest)
- 결과 Discord `#pr-알림` 채널으로 전송 (`DISCORD_WEBHOOK_CI`)

**CD (`.github/workflows/cd.yml`)**
- 트리거: main 브랜치 push
- lint → test → Docker Hub 빌드 & 푸시 → EC2 배포
- EC2 SSH 접근: 배포 시에만 22번 포트 임시 오픈 후 차단 (보안)
- Docker Hub: `odmd/vintage-house-reborn:latest`
- 배포 스크립트에 `set -e` 적용 — `git pull` 등 중간 명령 실패 시 즉시 중단되고 Discord에 실패로 표시됨 (예전엔 실패해도 성공으로 잘못 표시된 적 있음)
- DB 마이그레이션은 `docker-compose.prod.yml`의 `fastapi` 컨테이너 시작 명령어(`alembic upgrade head && uvicorn ...`)에 포함 — 배포될 때마다 자동 적용됨
- 결과 Discord `#배포-알림` 채널로 전송 (`DISCORD_WEBHOOK_CD`)

## 배포 서버 (AWS EC2)

- 인스턴스 중지 후 재시작하면 퍼블릭 IP 변경됨
- IP 변경 시 GitHub Secret `EC2_HOST` 업데이트 필요
- 접속: `ssh -i ~/.ssh/reborn.pem ubuntu@[IP]`
- pem 키 위치: `~/.ssh/reborn.pem`

## GitHub Secrets 목록

| Secret | 용도 |
|--------|------|
| `DOCKERHUB_USERNAME` | Docker Hub 계정 |
| `DOCKERHUB_TOKEN` | Docker Hub 토큰 |
| `EC2_HOST` | EC2 퍼블릭 IP (재시작 시 변경) |
| `EC2_SSH_KEY` | reborn.pem 내용 전체 |
| `AWS_ACCESS_KEY_ID` | IAM 액세스 키 (github-actions 유저) |
| `AWS_SECRET_ACCESS_KEY` | IAM 시크릿 키 |
| `AWS_REGION` | ap-northeast-2 |
| `SG_ID` | 보안 그룹 ID |
| `POSTGRES_DB` | DB 이름 |
| `POSTGRES_USER` | DB 유저 |
| `POSTGRES_PASSWORD` | DB 비밀번호 |
| `POSTGRES_HOST` | `db` (docker-compose 서비스명) |
| `POSTGRES_PORT` | `5432` |
| `REDIS_HOST` | `redis` (docker-compose 서비스명) |
| `REDIS_PORT` | `6379` |
| `REDIS_DB` | `0` |
| `REDIS_PASSWORD` | Redis 비밀번호 (requirepass) |
| `SECRET_KEY` | JWT 서명 키 |
| `ALGORITHM` | JWT 알고리즘 (`HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access Token 만료(분) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh Token 만료(일) |
| `SMTP_HOST` | `smtp.naver.com` |
| `SMTP_PORT` | `465` |
| `SMTP_USER` | 네이버 이메일 주소 |
| `SMTP_PASSWORD` | 네이버 애플리케이션 비밀번호 (로그인 비밀번호 아님) |
| `DISCORD_WEBHOOK_CI` | CI 결과 알림 웹훅 |
| `DISCORD_WEBHOOK_CD` | 배포 결과 알림 웹훅 |

`DATABASE_URL`/`REDIS_URL`은 Secret으로 관리하지 않음 (컴포넌트 조합 방식으로 변경, 위 참고). 토스페이먼츠 Secret은 코드 작성 후 추가 예정.

### Redis 보안
- `docker-compose.prod.yml`에서 Redis는 호스트에 포트 노출 안 함 (내부 docker network로만 접근)
- `command: sh -c "redis-server --requirepass $$REDIS_PASSWORD"`로 비밀번호 인증 필수화

## 개발 명령어

```bash
docker compose up --build        # 로컬 서버 실행
docker compose up --build -d     # 백그라운드 실행
make format                      # black + ruff
make type                        # mypy
make check                       # 전체 검사 (format + type + test)
```

## 컨벤션

- 모든 함수에 타입 힌트 필수 (mypy strict)
- 비동기 엔드포인트 사용 (async def)
- 에러 응답 포맷: `{"detail": "..."}`
- ruff lint 규칙: `E`(pycodestyle), `F`(pyflakes), `I`(import 정렬/isort) 활성화 (`pyproject.toml` `[tool.ruff.lint]`)
- Pydantic 검증 로직은 재사용 가능하면 `core/utils/validators.py`에 `Annotated[타입, AfterValidator(함수)]` 형태로 정의 (클래스로 감싸지 않음 — 상태 없는 순수 함수는 모듈 레벨 함수로 충분)
- 랜덤 값(OTP, 토큰 등)은 `random`이 아닌 `secrets` 모듈 사용 (암호학적으로 안전)
- Redis 키 네이밍은 앱별 `redis.py`에 클래스 메서드로 정의 (예: `EmailRedis.code(email)`)
- 테스트: `tests/` 디렉토리에 `app/` 구조 미러링, `pytest` + `pytest-asyncio`(`asyncio_mode = "auto"`), 라우터 테스트는 `tests/conftest.py`의 `client`(httpx `AsyncClient`) fixture 사용
- MVP 단계에서는 라우터(view) 테스트 위주로 작성, 모델 단위 테스트는 후순위
