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

## 배포

- **API 문서(운영)**: https://api.ohdimode.com/docs
- HTTPS(Let's Encrypt) + nginx 리버스 프록시, AWS EC2(Elastic IP 고정) 배포

## 주요 기능

- 이메일 인증 기반 회원가입
- 로그인 / 로그아웃 (JWT 액세스 토큰 + 리프레시 토큰, 로그아웃 시 액세스 토큰 블랙리스트)
- 리프레시 토큰으로 액세스 토큰 재발급
- 내 정보 조회 / 수정 / 회원 탈퇴 (`/me`)
- 관리자 권한 구분 (`User.is_admin`)
- 상품 CRUD (이미지 업로드는 S3 presigned URL 방식)
- 장바구니 (Redis, 담기/조회 — 개별 삭제·전체 비우기는 구현 예정)
- 결제 (토스페이먼츠) — 구현 예정

## API 엔드포인트

**인증** (`/api/v1/auth`)
```
POST    /api/v1/auth/send-email
POST    /api/v1/auth/verify-email
POST    /api/v1/auth/signup
POST    /api/v1/auth/login
POST    /api/v1/auth/logout
POST    /api/v1/auth/refresh
GET     /api/v1/auth/me
PATCH   /api/v1/auth/me
DELETE  /api/v1/auth/me
```

**상품** (`/api/v1/products`)
```
PUT     /api/v1/products/presigned-url
POST    /api/v1/products
GET     /api/v1/products
GET     /api/v1/products/{product_id}
PATCH   /api/v1/products/{product_id}
DELETE  /api/v1/products/{product_id}
```

**장바구니** (`/api/v1/cart`)
```
POST    /api/v1/cart/{product_id}
GET     /api/v1/cart
```

전체 요청/응답 스펙은 `/docs`(Swagger UI)에서 확인 가능합니다.

## 프로젝트 구조

```
app/
├── auth/                # 회원가입, 로그인/로그아웃, 토큰 재발급, 내 정보(/me), 이메일 인증
│   ├── router.py        # 엔드포인트 (라우팅 배선만)
│   ├── models.py        # User(is_admin 포함), RefreshToken
│   ├── dependencies.py  # 인증/권한 의존성 (get_user_id/get_user/get_admin_user), 다른 앱에서도 재사용
│   ├── schemas/         # 요청/응답 Pydantic 스키마 (기능별 분리: email.py, signup.py, me.py 등)
│   ├── services/        # 비즈니스 로직 (기능별 분리: email.py, signup.py, me.py 등)
│   └── utils/
│       ├── redis.py     # Redis 키 네이밍 (EmailRedis, LogoutRedis)
│       └── responses.py # 엔드포인트별 OpenAPI 에러 응답 문서
├── products/            # 상품 CRUD
│   └── models.py        # Product, ProductImage
├── cart/                # 장바구니 (Redis 기반, 테이블 없음)
├── payments/            # 결제 (토스페이먼츠)
│   └── models.py        # Order, OrderItem, Payment
├── core/                # 공용 기술
│   ├── config.py        # 환경변수 설정 (pydantic-settings)
│   ├── database.py      # SQLAlchemy async engine/session, BaseModel(ULID PK)
│   ├── redis.py          # Redis 비동기 클라이언트
│   └── utils/
│       ├── security.py   # OTP/토큰 생성, 비밀번호 해싱 함수
│       └── validators.py # 재사용 가능한 Pydantic 검증 타입 (EmailField 등)
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

필요한 환경변수 목록은 `env/example.env` 참고. `DATABASE_URL`/`REDIS_URL`은 직접 입력하지 않고, `POSTGRES_*`/`REDIS_*` 값들을 조합해서 `app/core/config.py`가 자동으로 만들어줌 (비밀번호 중복 저장으로 인한 불일치 방지).

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

새 앱에 모델을 추가하면 `alembic/env.py`에도 `import app.{app_name}.models`를 추가해야 alembic이 인식함.

## 데이터베이스 스키마

모든 모델은 공통으로 `id`(ULID, 26자), `created_at`, `updated_at`를 가짐 (`app/core/database.py`의 `BaseModel`).

| 테이블 | 설명 |
|---|---|
| `users` | 회원 정보 (email, nickname, address, is_admin 등) |
| `refresh_tokens` | JWT Refresh Token 저장 (해시값만 저장) |
| `products` | 상품 (빈티지 특성상 재고 없이 `status`로 판매 상태 관리) |
| `product_images` | 상품 이미지 (1:N, `order_number`로 노출 순서 관리) |
| `orders` | 주문 |
| `order_items` | 주문 상품 (구매 시점 가격 스냅샷 `price_at_purchase` 저장) |
| `payments` | 결제 내역 (토스페이먼츠 상태값 그대로 저장) |

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
