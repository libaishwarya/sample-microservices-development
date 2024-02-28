import unittest
import json
from main import app
# from routes.user import validate_email

class TestEndpoint(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
    
    def tearDown(self):
        pass
    
    def test_register_endpoint(self):
        data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'test_password'
        }
        response = self.app.post('/register', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
    
    def test_invalid_register(self):
        invalid_data = [{'name': 'test','password' : 'test_password'},
                {'name': 'test', 'email': 'test@gmail.com'},
                {'email': 'test@gmail.com','password' : 'test_password'}]
        for data in invalid_data:
            response = self.app.post('/register', data=json.dumps(data), content_type='application/json')
            self.assertTrue(response.status_code, 400)
        
    def test_login_endpoint(self):
        data = {
            'email': 'test@example.com',
            'password': 'test_password'
        }
        response = self.app.post('/login', data = json.dumps(data), content_type = 'application/json')
        self.assertEqual(response.status_code, 200)
        
    def test_invalid_login(self):
        invalid_data = [{'password' : 'test_password'},
                {'email': 'test@gmail.com'}]
        for data in invalid_data:
            response = self.app.post('/register', data=json.dumps(data), content_type='application/json')
            self.assertTrue(response.status_code, 400)
        

if __name__ == '__main__':
    unittest.main()
