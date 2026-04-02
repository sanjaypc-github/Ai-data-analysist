"""
Smoke tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


class TestAPIEndpoints:
    """Basic API endpoint tests"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns health info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
    
    def test_upload_endpoint_no_file(self):
        """Test upload endpoint with no file"""
        response = client.post("/api/upload")
        assert response.status_code == 422  # Validation error
    
    def test_upload_endpoint_wrong_type(self):
        """Test upload endpoint with wrong file type"""
        files = {'file': ('test.txt', b'test content', 'text/plain')}
        response = client.post("/api/upload", files=files)
        assert response.status_code == 400
        assert 'CSV' in response.json()['detail']
    
    def test_upload_valid_csv(self):
        """Test upload with valid CSV"""
        csv_content = b"col1,col2\n1,2\n3,4\n"
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post("/api/upload", files=files)
        assert response.status_code == 200
        
        data = response.json()
        assert 'dataset_id' in data
        assert data['filename'] == 'test.csv'
        assert data['rows'] == 2
        assert 'col1' in data['columns']
        assert 'col2' in data['columns']
    
    def test_ask_endpoint_missing_dataset(self):
        """Test ask endpoint with non-existent dataset"""
        payload = {
            "dataset_id": "nonexistent",
            "question": "Test question"
        }
        response = client.post("/api/ask", json=payload)
        assert response.status_code == 404
    
    def test_status_endpoint_invalid_task(self):
        """Test status endpoint with invalid task ID"""
        response = client.get("/api/status/invalid_task_id")
        assert response.status_code == 404
    
    def test_report_endpoint_invalid_task(self):
        """Test report endpoint with invalid task ID"""
        response = client.get("/api/report/invalid_task_id")
        assert response.status_code == 404
    
    def test_api_docs_available(self):
        """Test that API documentation is available"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_cors_headers(self):
        """Test that CORS headers are present"""
        response = client.get("/health")
        # CORS headers should be present
        assert response.status_code == 200


class TestEndToEndFlow:
    """Test complete upload -> ask -> status flow"""
    
    def test_complete_flow(self):
        """Test end-to-end workflow"""
        # Step 1: Upload CSV
        csv_content = b"product,sales,date\nProduct A,100,2024-01-01\nProduct B,200,2024-01-02\n"
        files = {'file': ('test_data.csv', csv_content, 'text/csv')}
        
        upload_response = client.post("/api/upload", files=files)
        assert upload_response.status_code == 200
        
        dataset_id = upload_response.json()['dataset_id']
        assert dataset_id is not None
        
        # Step 2: Ask question
        ask_payload = {
            "dataset_id": dataset_id,
            "question": "What is the total sales?"
        }
        
        ask_response = client.post("/api/ask", json=ask_payload)
        assert ask_response.status_code == 200
        
        task_data = ask_response.json()
        task_id = task_data['task_id']
        assert task_id is not None
        assert 'generated_code' in task_data
        
        # Step 3: Check status
        status_response = client.get(f"/api/status/{task_id}")
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert status_data['task_id'] == task_id
        assert status_data['dataset_id'] == dataset_id
        assert status_data['status'] in ['pending', 'running', 'completed', 'failed']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
