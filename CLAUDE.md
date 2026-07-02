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

`env/.env` 파일 사용 (docker compose가 컨테이너에 주입)

```
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
DATABASE_URL=
REDIS_URL=
SECRET_KEY=
ALGORITHM=
ACCESS_TOKEN_EXPIRE_MINUTES=
REFRESH_TOKEN_EXPIRE_DAYS=
TOSS_SECRET_KEY=
TOSS_CLIENT_KEY=
```

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
| `DATABASE_URL` | PostgreSQL 연결 URL |
| `REDIS_URL` | Redis 연결 URL |
| `DISCORD_WEBHOOK_CI` | CI 결과 알림 웹훅 |
| `DISCORD_WEBHOOK_CD` | 배포 결과 알림 웹훅 |

JWT, 토스페이먼츠 Secret은 코드 작성 후 추가 예정

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
