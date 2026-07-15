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
├── router.py       # 엔드포인트 (라우팅 배선만, 문서/에러 정의는 utils/responses.py로)
├── models.py       # SQLAlchemy 모델
├── schemas/        # 요청/응답 Pydantic 스키마 (기능별로 파일 분리, 예: schemas/signup.py)
├── services/       # 비즈니스 로직 (기능별로 파일 분리, 예: services/signup.py)
├── dependencies.py # 다른 앱에서도 재사용하는 FastAPI Depends 함수 (인증/권한 검사 등)
└── utils/
    ├── responses.py  # 엔드포인트별 OpenAPI 에러 응답 문서 (status code → 설명/예시)
    └── redis.py       # Redis 키 네이밍 (앱별로 있는 경우, 예: EmailRedis)
```

### 인증/권한 의존성 (`app/auth/dependencies.py`)
Django의 `permission_classes`에 대응하는 FastAPI 방식. 3단계로 쌓아서 재사용:
- `get_user_id` — JWT 서명/만료/블랙리스트만 검증, DB 접근 없이 `user_id`(str) 반환 (제일 가벼움)
- `get_user` — `get_user_id` 위에서 DB 조회까지 해서 `User` 객체 반환 (`/me`처럼 로그인한 유저 본인 데이터 다룰 때)
- `get_admin_user` — `get_user` 위에서 `is_admin` 검사까지 (상품 생성/수정/삭제처럼 관리자 전용 엔드포인트에서 사용)

이름 규칙: `_id`가 붙으면 DB 조회 없이 가벼운 것, 안 붙으면 DB까지 가서 객체를 반환하는 것. 읽기 전용(누구나/로그인 유저) 엔드포인트는 별도 의존성 없이 `get_user_id`를 그대로 쓰거나 아예 의존성 없이 공개하고, 쓰기(관리자 전용) 엔드포인트만 `get_admin_user`를 붙이면 됨 — "권한 구분"은 의존성 종류가 아니라 "어떤 엔드포인트에 어떤 의존성을 붙이느냐"로 결정됨.

`router.py`는 앱 전체에서 하나로 유지 (엔드포인트 함수는 배선만 하는 얇은 코드라 파일이 커져도 가독성 문제가 적음). `schemas/`, `services/`는 기능(엔드포인트) 단위로 나눠서, 관련 로직/스키마가 한 파일에 응집되게 함.

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
- `User.is_admin`(기본값 `False`)으로 관리자 여부 구분. 관리자 지정은 API로 하지 않고 DB에 직접 접속해서 수동으로 값 변경 (누구나 자기 자신을 관리자로 만들 수 있는 엔드포인트는 그 자체로 보안 구멍)
- 부모 없이 존재 의미 없는 자식 테이블(RefreshToken, ProductImage, OrderItem, Payment 등)은 FK에 `ondelete="CASCADE"` 필수
- 새 모델 추가 시 `alembic/env.py`에 `import app.{app}.models` 추가해야 autogenerate가 인식함
- 비밀번호 등 민감정보는 **저장 위치를 하나로 통일** (예: `DATABASE_URL`을 별도 값으로 안 두고 `POSTGRES_PASSWORD` 등 컴포넌트에서 조합 — 중복 저장 시 값이 어긋나는 사고 경험함)
- URL에 비밀번호를 조합할 때는 `urllib.parse.quote()`로 이스케이프 (비밀번호에 `/`, `+` 등 특수문자 포함 시 URL 파싱이 깨짐)

## 구현 현황

**완료**
- 인증: 이메일 인증 발송/검증(OTP), 회원가입, 로그인/로그아웃(JWT + 블랙리스트), 토큰 재발급, `/me`(조회/수정/탈퇴)
- 권한: `User.is_admin` + 3단계 의존성(`get_user_id`/`get_user`/`get_admin_user`)
- 인프라: Docker Compose(로컬/서버), CI(lint+test), CD(빌드→배포), nginx+Let's Encrypt HTTPS, EC2 Elastic IP

**진행 예정 (다음 작업)**
- 상품 CRUD (`app/products/`) — 관리자 전용 생성/수정/삭제(`get_admin_user`), 조회는 공개
- 상품 이미지 업로드 — AWS S3 Presigned URL 발급 방식 (서버 부하 없이 클라이언트 직접 업로드)
- 장바구니 (`app/cart/`, Redis 기반, 테이블 없음)
- 결제 (`app/payments/`, 토스페이먼츠)

**MVP 이후로 미룸**
- 비밀번호 변경/재설정
- 이메일 인증 코드 대조 시도 횟수 제한(rate limiting)

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

| 환경 | FastAPI | PostgreSQL | Redis | 공개 포트 |
|------|---------|------------|-------|-----------|
| 로컬 | 8001 | 5434 | 6480 | 8001 (직접 접근) |
| 서버 | 8000 (내부 전용) | 5432 | 6379 | 80/443 (nginx 경유, 8000은 외부 비공개) |

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
- `docker-compose.prod.yml` — 서버 배포용 (Docker Hub 이미지, restart: always). `db`/`redis`/`fastapi` 외에 `nginx`(리버스 프록시+HTTPS), `certbot`(인증서 갱신용, 상시 실행 아님) 서비스 포함
- EC2에서는 `docker-compose`(하이픈) v2 사용 (`/usr/local/bin/docker-compose`)
- **알려진 이슈**: `docker-compose.yml`이 `.:/app`으로 프로젝트 전체(`.venv` 포함)를 바인드 마운트해서, 호스트에서 `uv run`을 직접 돌리면(예: 스크립트 검증) 컨테이너의 `.venv`와 충돌해 개발 패키지(mypy 등)가 깨질 수 있음 — 증상 발생 시 `docker compose exec fastapi uv sync --all-groups`(필요하면 `--reinstall`)로 복구. 근본적으로는 `.venv`를 익명 볼륨(`/app/.venv`)으로 분리하면 해결되지만, 아직 반영 안 함

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

- 탄력적 IP(Elastic IP) 연결해둠 → 인스턴스 재시작해도 퍼블릭 IP 안 바뀜 (예전엔 재시작마다 바뀌어서 `EC2_HOST` 매번 갱신해야 했음)
- 접속: `ssh -i ~/.ssh/reborn.pem ubuntu@[Elastic IP]`
- pem 키 위치: `~/.ssh/reborn.pem`

## 도메인 / HTTPS (nginx + Let's Encrypt)

- 도메인: `api.ohdimode.com` (가비아 구매, A 레코드 → EC2 Elastic IP)
- `ohdimode.com`은 개인 브랜드 도메인 — 루트는 추후 포트폴리오 허브용으로 남겨두고, 프로젝트별로 서브도메인 사용 (예: 다른 프로젝트는 `다른이름.ohdimode.com`)
- EC2에 nginx를 리버스 프록시로 두고, fastapi 컨테이너는 8000번 포트를 외부에 직접 노출하지 않음 (보안그룹에서도 8000 닫음, nginx만 80/443 공개)
- 인증서는 Let's Encrypt(`certbot`), `docker-compose.prod.yml`에 `nginx`/`certbot` 서비스로 정의 (설정 파일: `nginx/nginx.conf`, 인증서/webroot는 `certbot_conf`/`certbot_www` 도커 볼륨에 저장돼서 재배포해도 유지됨)
- **최초 인증서 발급은 수동**(닭-달걀 문제: nginx가 인증서 파일을 참조해야 뜨는데, 인증서 받으려면 nginx가 먼저 떠서 80번에 응답해야 함) — SSL 없는 임시 nginx 설정으로 먼저 띄운 뒤 `certbot certonly --webroot`로 발급받고 정식 설정으로 교체하는 절차 필요
- 인증서 자동 갱신은 EC2의 **cron**(앱 CD 파이프라인과는 별개, 서버 자체의 정기 작업)으로 등록: 매일 새벽 3시 `certbot renew` + nginx 재시작
- 보안그룹: 80/443은 `0.0.0.0/0`(누구나, Let's Encrypt 검증 서버도 포함), 22(SSH)는 특정 IP로만 제한

## GitHub Secrets 목록

| Secret | 용도 |
|--------|------|
| `DOCKERHUB_USERNAME` | Docker Hub 계정 |
| `DOCKERHUB_TOKEN` | Docker Hub 토큰 |
| `EC2_HOST` | EC2 탄력적 IP (재시작해도 안 바뀜) |
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
| `S3_BUCKET_NAME` | 상품 이미지 버킷 이름 (`vintage-house-reborn-images`) |
| `S3_REGION` | `ap-northeast-2` |
| `S3_ACCESS_KEY_ID` | IAM 액세스 키 (`vintage-house-app` 유저, 해당 버킷 전용 최소 권한) |
| `S3_SECRET_ACCESS_KEY` | IAM 시크릿 키 (`vintage-house-app` 유저) |
| `DISCORD_WEBHOOK_CI` | CI 결과 알림 웹훅 |
| `DISCORD_WEBHOOK_CD` | 배포 결과 알림 웹훅 |

`DATABASE_URL`/`REDIS_URL`은 Secret으로 관리하지 않음 (컴포넌트 조합 방식으로 변경, 위 참고). 토스페이먼츠 Secret은 코드 작성 후 추가 예정.

`S3_ACCESS_KEY_ID`/`S3_SECRET_ACCESS_KEY`는 EC2 배포용 `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`(github-actions 유저)와 별개 — 최소 권한 원칙상 이 버킷에만 접근 가능한 전용 IAM 유저(`vintage-house-app`)의 키를 사용함.

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
- Redis 키 네이밍은 앱별 `utils/redis.py`에 클래스 메서드로 정의 (예: `EmailRedis.code(email)`)
- 테스트: `tests/` 디렉토리에 `app/` 구조 미러링, `test_routers/`/`test_schemas/`/`test_services/` 하위 폴더에 기능(엔드포인트) 단위로 파일 분리 (예: `test_routers/test_signup.py`). `pytest` + `pytest-asyncio`(`asyncio_mode = "auto"`), 라우터 테스트는 `tests/conftest.py`의 `client`(httpx `AsyncClient`) fixture 사용
- `unittest.mock.patch("app.auth.services.email.send_email", ...)`처럼 모듈 경로를 문자열로 지정하는 곳은 리팩토링/파일 이동 시 정적 분석 도구가 못 잡아주니 수동으로 같이 고쳐야 함 (실제로 `service/` → `services/` 리네임 때 `conftest.py`의 `patch()` 경로만 누락되어 테스트가 깨졌던 적 있음)
- MVP 단계에서는 라우터(view) 테스트 위주로 작성, 모델 단위 테스트는 후순위
