# backend/apps/api/tests/test_images.py

import pytest
from src.models.image import Image

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
        response = client.get("/images/originals/../../../etc/passwd")
        
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


class TestListMyImages:
    """GET /images 엔드포인트 테스트 (본인 이미지 목록)"""
    
    def test_list_my_images_empty(self, client, db):
        """이미지가 없을 때 테스트"""
        response = client.get("/images")
        
        assert response.status_code == 200
        data = response.json()
        assert data["images"] == []
        assert data["count"] == 0
    
    def test_list_my_images_with_data(self, client, db, mock_s3_client):
        """본인 이미지 목록 조회 테스트"""
        # DB에 테스트 이미지 추가 (user_id=1, mock_get_current_user가 반환하는 값)
        image1 = Image(
            user_id=1,
            object_key="originals/test1.jpg",
            filename="test1.jpg",
            content_type="image/jpeg",
            size=1024
        )
        image2 = Image(
            user_id=1,
            object_key="originals/test2.jpg",
            filename="test2.jpg",
            content_type="image/png",
            size=2048
        )
        db.add(image1)
        db.add(image2)
        db.commit()
        
        response = client.get("/images")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["images"]) == 2
        
        # 첫 번째 이미지 검증
        img = data["images"][0]
        assert "id" in img
        assert "key" in img
        assert "filename" in img
        assert "size" in img
        assert "url" in img  # Presigned URL
        assert "created_at" in img
    
    def test_list_my_images_only_own(self, client, db):
        """다른 사용자 이미지는 제외되는지 테스트"""
        # user_id=1 (본인)
        image1 = Image(
            user_id=1,
            object_key="originals/my-image.jpg",
            filename="my-image.jpg",
            content_type="image/jpeg",
            size=1024
        )
        # user_id=2 (다른 사용자)
        image2 = Image(
            user_id=2,
            object_key="originals/other-image.jpg",
            filename="other-image.jpg",
            content_type="image/jpeg",
            size=2048
        )
        db.add_all([image1, image2])
        db.commit()
        
        response = client.get("/images")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1  # 본인 이미지만
        assert data["images"][0]["filename"] == "my-image.jpg"
    
    def test_list_my_images_pagination(self, client, db):
        """페이지네이션 테스트"""
        # 5개 이미지 추가
        for i in range(5):
            img = Image(
                user_id=1,
                object_key=f"originals/test{i}.jpg",
                filename=f"test{i}.jpg",
                content_type="image/jpeg",
                size=1024
            )
            db.add(img)
        db.commit()
        
        # skip=2, limit=2
        response = client.get("/images?skip=2&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["images"]) == 2


class TestListUserImages:
    """GET /images/{user_id} 엔드포인트 테스트 (특정 사용자 이미지)"""
    
    def test_list_user_images(self, client, db):
        """특정 사용자 이미지 목록 조회 테스트"""
        # user_id=2의 이미지 추가
        image1 = Image(
            user_id=2,
            object_key="originals/user2-image1.jpg",
            filename="user2-image1.jpg",
            content_type="image/jpeg",
            size=1024
        )
        image2 = Image(
            user_id=2,
            object_key="originals/user2-image2.jpg",
            filename="user2-image2.jpg",
            content_type="image/jpeg",
            size=2048
        )
        # user_id=3의 이미지 (제외되어야 함)
        image3 = Image(
            user_id=3,
            object_key="originals/user3-image.jpg",
            filename="user3-image.jpg",
            content_type="image/jpeg",
            size=512
        )
        db.add_all([image1, image2, image3])
        db.commit()
        
        response = client.get("/images/user/2")  # user_id=2
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["images"]) == 2
        
        # 모든 이미지가 user_id=2인지 확인
        filenames = [img["filename"] for img in data["images"]]
        assert "user2-image1.jpg" in filenames
        assert "user2-image2.jpg" in filenames
        assert "user3-image.jpg" not in filenames
    
    def test_list_user_images_empty(self, client, db):
        """이미지가 없는 사용자 테스트"""
        response = client.get("/images/user/999")  # 존재하지 않는 사용자
        
        assert response.status_code == 200
        data = response.json()
        assert data["images"] == []
        assert data["count"] == 0


class TestListAllImages:
    """GET /images/public 엔드포인트 테스트 (모든 이미지)"""
    
    def test_list_all_images(self, client, db):
        """모든 사용자 이미지 목록 조회 테스트"""
        # 여러 사용자의 이미지 추가
        image1 = Image(
            user_id=1,
            object_key="originals/user1-image.jpg",
            filename="user1-image.jpg",
            content_type="image/jpeg",
            size=1024
        )
        image2 = Image(
            user_id=2,
            object_key="originals/user2-image.jpg",
            filename="user2-image.jpg",
            content_type="image/jpeg",
            size=2048
        )
        image3 = Image(
            user_id=3,
            object_key="originals/user3-image.jpg",
            filename="user3-image.jpg",
            content_type="image/jpeg",
            size=512
        )
        db.add_all([image1, image2, image3])
        db.commit()
        
        response = client.get("/images/public")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3
        assert len(data["images"]) == 3
        
        # user_id 필드 확인
        for img in data["images"]:
            assert "user_id" in img
            assert "id" in img
            assert "url" in img
    
    def test_list_all_images_includes_all_users(self, client, db):
        """모든 사용자의 이미지가 포함되는지 확인"""
        # user_id 1, 2, 3의 이미지 추가
        for user_id in [1, 2, 3]:
            img = Image(
                user_id=user_id,
                object_key=f"originals/user{user_id}.jpg",
                filename=f"user{user_id}.jpg",
                content_type="image/jpeg",
                size=1024
            )
            db.add(img)
        db.commit()
        
        response = client.get("/images/public")
        
        assert response.status_code == 200
        data = response.json()
        
        user_ids = [img["user_id"] for img in data["images"]]
        assert 1 in user_ids
        assert 2 in user_ids
        assert 3 in user_ids
    
    def test_list_all_images_pagination(self, client, db):
        """공개 이미지 페이지네이션 테스트"""
        # 10개 이미지 추가
        for i in range(10):
            img = Image(
                user_id=1,
                object_key=f"originals/image{i}.jpg",
                filename=f"image{i}.jpg",
                content_type="image/jpeg",
                size=1024
            )
            db.add(img)
        db.commit()
        
        # skip=3, limit=5
        response = client.get("/images/public?skip=3&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 5
        assert len(data["images"]) == 5
    
    def test_list_all_images_empty(self, client, db):
        """이미지가 하나도 없을 때 테스트"""
        response = client.get("/images/public")
        
        assert response.status_code == 200
        data = response.json()
        assert data["images"] == []
        assert data["count"] == 0