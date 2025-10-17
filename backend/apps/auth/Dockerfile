# apps/auth/Dockerfile
FROM python:3.11-slim as base

# Python 출력 버퍼링 방지
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# 작업 디렉토리
WORKDIR /app

# 시스템 패키지 설치 (PostgreSQL 클라이언트 라이브러리 포함)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY apps/auth/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /app/requirements.txt

# ===== Test Stage =====
FROM base as test
COPY apps/auth/ /app/
CMD ["pytest", "tests/", "-v"]

# ===== Production Stage =====
FROM base as production

# 소스 코드만 복사
COPY apps/auth/src /app/src

# 포트 노출
EXPOSE 8000

# 서버 실행
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]