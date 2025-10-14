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
# 기본 (.env 파일)
docker compose up -d

# 개발 (.env.local)
docker compose --env-file .env.local up -d

# 운영 (.env.prod)
docker compose --env-file .env.prod up -d

#docker compose --profile infra --profile api up -d --build
# docker compose --profile infra --profile api up -d
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

## 🚀 업로드 시나리오

이 서버는 **Presigned URL 방식**을 사용합니다.  
즉, API 서버는 파일 자체를 받지 않고 **임시로 유효한 업로드 URL**을 발급해 주며,  
클라이언트(또는 curl)가 해당 URL로 S3/MinIO에 직접 업로드합니다.

---

### 1) Presigned URL 발급 (POST /uploads)

```bash
curl -X POST http://localhost:8080/uploads   -H "Content-Type: application/json"   -d '{"filename":"cat.jpg","contentType":"image/jpeg","size":123456}'
```

✅ 성공 시 응답 예시:
```json
{
  "presignedUrl": "http://localhost:9000/uploads/abc123.jpg?...",
  "objectKey": "uploads/abc123.jpg"
}
```

- **검증 로직**
  - 허용 확장자: JPG, PNG, WebP, AVIF (옵션: GIF)
  - 허용 MIME: `image/jpeg`, `image/png`, `image/webp`, `image/avif`
  - 최대 크기: 10MB

- **실패 시**
  - 10MB 초과 → `400 File too large`
  - 확장자/타입 불일치 → `400 Unsupported file type`

---

### 2) Presigned URL로 직접 업로드 (PUT)

```bash
curl -X PUT "<presignedUrl>"   -H "Content-Type: image/jpeg"   --data-binary @cat.jpg
```

- 요청은 API 서버를 거치지 않고 **MinIO(S3)** 로 바로 전송됩니다.
- MinIO 콘솔(http://localhost:9001)에서 `uploads/` 버킷 안에 업로드된 객체를 확인할 수 있습니다.

---

### 3) 조회 Presigned URL 발급 (GET /images/:key) [선택]

```bash
curl "http://localhost:8080/images/uploads/abc123.jpg"
```

✅ 성공 시 응답 예시:
```json
{
  "url": "http://localhost:9000/uploads/abc123.jpg?...",
  "key": "uploads/abc123.jpg",
  "expiresIn": 900,
  "download": false
}
```

- `as_download=true&filename=cat.jpg` 옵션으로 다운로드 강제 가능:
```bash
curl "http://localhost:8080/images/uploads/abc123.jpg?as_download=true&filename=cat.jpg"
```

### test_upload.sh를 통한 테스트

1. brew install jq 등으로 jq 설치
2. chmod +x test_upload.sh
3. ./test_upload.sh

### MinIO 콘솔에서 확인

1. [MinIO 콘솔](http://localhost:9001)
2. 로그인(minio / minio123) 
3. uploads 버킷에서 이미지 확인

---

## 🔑 업로드 과정 요약

1. 클라이언트가 **API 서버에 업로드 요청** → Presigned PUT URL 발급
2. 클라이언트가 **Presigned URL로 직접 PUT 업로드** → MinIO에 저장
3. 필요 시 **조회용 Presigned GET URL 발급** → 제한 시간 동안만 다운로드 가능

---

## 🔗 참고
- **MinIO Console**: http://localhost:9001  
- **API 서버**: http://localhost:8080  
- 기본 MinIO 계정: `minio / minio123`

---

## To-Do

- Redis
- CloudFlare
- Jenkins 등 CI/CD
- S3 전환