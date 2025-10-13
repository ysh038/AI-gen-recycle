# Image Upload MVP

간단한 **이미지 업로드 서버 + S3 호환 스토리지(MinIO)** 아키텍처입니다.  
추후 확장을 고려해 `apps/` 디렉토리 안에 서비스 단위로 추가할 수 있습니다.

---

## 📁 디렉토리 구조

```
repo/
  docker-compose.yml          # ✅ 통합 compose (infra + api 한 방에)
  .env                        # (선택) 공통 환경변수
  apps/
    api/
      Dockerfile
      src/
        server.(ts|py)        # API 엔트리포인트
```

---

## 🧩 docker-compose.yml (루트 통합)

```yaml
name: image-mvp

services:
  # ---- Infra (MinIO) ----
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER:-minio}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD:-minio123}
    ports:
      - "9000:9000"   # S3 API
      - "9001:9001"   # 콘솔
    volumes:
      - minio-data:/data
    networks: [ shared ]
    profiles: [ infra ]

  # ---- App (API) ----
  api:
    build:
      context: .
      dockerfile: apps/api/Dockerfile
    environment:
      S3_ENDPOINT: http://minio:9000
      S3_ACCESS_KEY: ${MINIO_ROOT_USER:-minio}
      S3_SECRET_KEY: ${MINIO_ROOT_PASSWORD:-minio123}
      S3_BUCKET: uploads
      PORT: 8080
    ports:
      - "8080:8080"
    depends_on:
      - minio
    networks: [ shared ]
    profiles: [ api ]

networks:
  shared:

volumes:
  minio-data:
```

---

## ▶️ 실행 시나리오 (원하는 것만 켜고/끄는 법)

### 1) 전부 실행 (MinIO + API)
```bash
docker compose --profile infra --profile api up -d --build
```

### 2) 인프라만 실행 (MinIO만)
```bash
docker compose --profile infra up -d
```

### 3) API만 실행 (MinIO가 이미 켜져있을 경우)
```bash
docker compose --profile api up -d --build api
```

### 4) API만 재시작 / 재빌드
```bash
# 코드만 수정했을 때
docker compose restart api

# Dockerfile/의존성까지 바뀌었을 때
docker compose build api && docker compose up -d api
```

### 5) 특정 서비스만 종료
```bash
docker compose stop api
docker compose rm -f api
```

---

## 🔗 참고
- **MinIO Console**: http://localhost:9001  
- **API 서버**: http://localhost:8080  
- 기본 MinIO 계정: `minio / minio123`
