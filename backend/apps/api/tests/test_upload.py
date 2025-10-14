import pytest
from unittest.mock import patch, MagicMock

class TestUploadEndpoint:
    """POST /uploads 엔드포인트 테스트"""
    
    def test_presigned_url_success(self, client, mock_s3_client):
        """정상적인 presigned URL 발급 테스트"""
        payload = {
            "filename": "test.jpg",
            "contentType": "image/jpeg",
            "size": 1024 * 1024  # 1MB
        }
        
        response = client.post("/uploads", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "presignedUrl" in data
        assert "objectKey" in data
        assert data["objectKey"].startswith("originals/")
        assert data["objectKey"].endswith(".jpg")
    
    def test_file_too_large(self, client):
        """파일 크기 초과 테스트"""
        payload = {
            "filename": "large.jpg",
            "contentType": "image/jpeg",
            "size": 11 * 1024 * 1024  # 11MB (최대 10MB)
        }
        
        response = client.post("/uploads", json=payload)
        
        assert response.status_code == 400
        assert "File too large" in response.json()["detail"]
    
    def test_unsupported_file_type(self, client):
        """지원하지 않는 파일 형식 테스트"""
        payload = {
            "filename": "test.pdf",
            "contentType": "application/pdf",
            "size": 1024
        }
        
        response = client.post("/uploads", json=payload)
        
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]
    
    @pytest.mark.parametrize("filename,content_type", [
        ("image.jpg", "image/jpeg"),
        ("image.png", "image/png"),
        ("image.webp", "image/webp"),
        ("image.avif", "image/avif"),
    ])
    def test_allowed_file_types(self, client, mock_s3_client, filename, content_type):
        """허용된 파일 형식들 테스트"""
        payload = {
            "filename": filename,
            "contentType": content_type,
            "size": 1024
        }
        
        response = client.post("/uploads", json=payload)
        
        assert response.status_code == 200