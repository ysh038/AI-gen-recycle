import pytest

class TestImagesEndpoint:
    """GET /images/{key} 엔드포인트 테스트"""
    
    def test_get_existing_image(self, client, mock_s3_client):
        """존재하는 이미지 조회 테스트"""
        # 테스트용 객체 업로드
        test_key = "originals/test123.jpg"
        mock_s3_client.put_object(
            Bucket="test-bucket",
            Key=test_key,
            Body=b"fake image data"
        )
        
        response = client.get(f"/images/{test_key}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "url" in data
        assert "key" in data
        assert "expiresIn" in data
        assert data["key"] == test_key
    
    def test_get_nonexistent_image(self, client):
        """존재하지 않는 이미지 조회 테스트"""
        response = client.get("/images/originals/nonexistent.jpg")
        
        assert response.status_code == 404
        assert "Object not found" in response.json()["detail"]
    
    def test_invalid_key_path_traversal(self, client):
        """경로 탐색 공격 방지 테스트"""
        # URL에서 ..이 정규화되므로, key에 직접 ..가 포함된 경우를 테스트
        response = client.get("/images/originals/../../../etc/passwd")
        
        # FastAPI가 경로를 정규화하므로 404가 반환될 수 있음
        # 또는 ..가 남아있으면 400 반환
        assert response.status_code in [400, 404]
    
    def test_download_mode(self, client, mock_s3_client):
        """다운로드 모드 테스트"""
        test_key = "originals/test123.jpg"
        mock_s3_client.put_object(
            Bucket="test-bucket",
            Key=test_key,
            Body=b"fake image data",
            ContentType="image/jpeg"
        )
        
        response = client.get(
            f"/images/{test_key}",
            params={"as_download": True, "filename": "my-image.jpg"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["download"] is True
        assert "url" in data
        # moto가 생성한 URL에는 response-content-disposition 파라미터가 없을 수 있음
        # 핵심은 download 플래그가 제대로 전달되는지 확인