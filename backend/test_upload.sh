#!/usr/bin/env bash
# test_upload.sh - OAuth + 이미지 업로드 통합 테스트
set -euo pipefail

API_BASE="${API_BASE:-http://localhost:8080}"
AUTH_BASE="${AUTH_BASE:-http://localhost:8001}"
IMG_FILE="${IMG_FILE:-test.jpg}"
TEST_EMAIL="${TEST_EMAIL:-test@example.com}"

if ! command -v jq >/dev/null 2>&1; then
  echo "❌ jq가 필요합니다. (brew install jq / apt-get install jq)" >&2
  exit 1
fi

if [ ! -f "$IMG_FILE" ]; then
  echo "❌ 이미지 파일이 없습니다: $IMG_FILE" >&2
  exit 1
fi

# 파일 크기 계산
SIZE=$(wc -c < "$IMG_FILE" | tr -d ' ')

echo "================================"
echo "🔐 1) OAuth 테스트 토큰 발급..."
echo "================================"

AUTH_RESP=$(curl -sS -f -X POST "$AUTH_BASE/auth/oauth/test-token?email=$TEST_EMAIL" \
  -H "Content-Type: application/json")

echo "Auth Response: $AUTH_RESP"

ACCESS_TOKEN=$(echo "$AUTH_RESP" | jq -r .access_token)
USER_ID=$(echo "$AUTH_RESP" | jq -r .user.user_id)

if [ -z "$ACCESS_TOKEN" ] || [ "$ACCESS_TOKEN" = "null" ]; then
  echo "❌ JWT 토큰 발급 실패" >&2
  exit 1
fi

echo "✅ JWT Token: ${ACCESS_TOKEN:0:50}..."
echo "✅ User ID: $USER_ID"
echo ""

echo "================================"
echo "🔑 2) JWT 토큰 검증..."
echo "================================"

VERIFY_RESP=$(curl -sS -f -X POST "$AUTH_BASE/auth/verify" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Verify Response: $VERIFY_RESP"
echo ""

echo "================================"
echo "📤 3) Presigned URL 발급..."
echo "================================"

# 인증이 필요하다면 -H "Authorization: Bearer $ACCESS_TOKEN" 추가
RESP=$(curl -sS -f -X POST "$API_BASE/uploads" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{\"filename\":\"$(basename "$IMG_FILE")\",\"contentType\":\"image/png\",\"size\":$SIZE}")

echo "Response: $RESP"
URL=$(echo "$RESP" | jq -r .presignedUrl)
KEY=$(echo "$RESP" | jq -r .objectKey)

if [ -z "$URL" ] || [ "$URL" = "null" ]; then
  echo "❌ presignedUrl 파싱 실패" >&2
  exit 1
fi

echo "✅ Presigned URL: ${URL:0:100}..."
echo "✅ Object Key: $KEY"
echo ""

echo "================================"
echo "📤 4) S3에 이미지 업로드..."
echo "================================"

curl --fail-with-body -sS -X PUT "$URL" \
  -H "Content-Type: image/png" \
  --data-binary @"$IMG_FILE" \
  -D - >/dev/null

echo "✅ Upload OK."
echo ""

echo "================================"
echo "📥 5) 조회용 Presigned URL 발급..."
echo "================================"

# 인증이 필요하다면 -H "Authorization: Bearer $ACCESS_TOKEN" 추가
RESP2=$(curl -sS -f "$API_BASE/images/$KEY" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Response: $RESP2"
GET_URL=$(echo "$RESP2" | jq -r .url)
echo "✅ View URL: $GET_URL"
echo ""

echo "================================"
echo "👤 6) 내 정보 조회..."
echo "================================"

ME_RESP=$(curl -sS -f "$AUTH_BASE/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Me Response: $ME_RESP"
echo ""

echo "================================"
echo "✅ 모든 테스트 완료!"
echo "================================"
echo "📊 요약:"
echo "  - 사용자: $TEST_EMAIL (ID: $USER_ID)"
echo "  - 업로드: $KEY"
echo "  - 조회 URL: $GET_URL"