#!/usr/bin/env bash
# test_upload.sh
set -euo pipefail

API_BASE="${API_BASE:-http://localhost:8080}"
IMG_FILE="${IMG_FILE:-test.jpg}"

if ! command -v jq >/dev/null 2>&1; then
  echo "jq가 필요합니다. (brew install jq / apt-get install jq)" >&2
  exit 1
fi

if [ ! -f "$IMG_FILE" ]; then
  echo "이미지 파일이 없습니다: $IMG_FILE (현재 디렉토리에 test.jpg를 두거나 IMG_FILE로 지정하세요)" >&2
  exit 1
fi

# ✅ OS에 상관없이 동작하는 파일 크기 계산 (bytes)
SIZE=$(wc -c < "$IMG_FILE" | tr -d ' ')

echo "🔹 1) Presigned URL 발급..."
RESP=$(curl -sS -f -X POST "$API_BASE/uploads" \
  -H "Content-Type: application/json" \
  -d "{\"filename\":\"$(basename "$IMG_FILE")\",\"contentType\":\"image/png\",\"size\":$SIZE}")

echo "Response: $RESP"
URL=$(echo "$RESP" | jq -r .presignedUrl)
KEY=$(echo "$RESP" | jq -r .objectKey)

if [ -z "$URL" ] || [ "$URL" = "null" ]; then
  echo "presignedUrl 파싱 실패" >&2
  exit 1
fi

echo "Presigned URL: $URL"
echo "Object Key: $KEY"

echo "🔹 2) Presigned URL로 업로드..."
curl --fail-with-body -sS -X PUT "$URL" \
  -H "Content-Type: image/png" \
  --data-binary @"$IMG_FILE" \
  -D - >/dev/null
echo "Upload OK."

echo "🔹 3) 조회용 Presigned URL 발급..."
RESP2=$(curl -sS -f "$API_BASE/images/$KEY")
echo "Response: $RESP2"
GET_URL=$(echo "$RESP2" | jq -r .url)
echo "View URL: $GET_URL"
