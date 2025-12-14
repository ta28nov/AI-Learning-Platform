"""
Test Variables - Centralized storage for test data
Tương tự như Postman Environment Variables

Sử dụng:
    from tests.test_variables import TestVariables
    
    # Trong test:
    vars = TestVariables()
    await vars.setup(client, test_users)  # Setup một lần
    
    # Sử dụng:
    headers = vars.get_headers("student")
    course_id = vars.course_id
"""

from typing import Dict, Any, Optional
from httpx import AsyncClient


class TestVariables:
    """
    Centralized test variables storage.
    Lưu trữ tokens, IDs và các biến test dùng chung.
    """
    
    def __init__(self):
        # Authentication Tokens
        self.admin_token: Optional[str] = None
        self.instructor1_token: Optional[str] = None
        self.instructor2_token: Optional[str] = None
        self.student1_token: Optional[str] = None
        self.student2_token: Optional[str] = None
        self.student3_token: Optional[str] = None
        
        # User IDs
        self.admin_user_id: Optional[str] = None
        self.instructor1_user_id: Optional[str] = None
        self.instructor2_user_id: Optional[str] = None
        self.student1_user_id: Optional[str] = None
        self.student2_user_id: Optional[str] = None
        
        # Course & Learning
        self.course_id: Optional[str] = None
        self.module_id: Optional[str] = None
        self.lesson_id: Optional[str] = None
        self.quiz_id: Optional[str] = None
        self.enrollment_id: Optional[str] = None
        self.personal_course_id: Optional[str] = None
        
        # Assessment
        self.assessment_session_id: Optional[str] = None
        
        # Chat
        self.conversation_id: Optional[str] = None
        
        # Class Management
        self.class_id: Optional[str] = None
        self.invite_code: Optional[str] = None
        
        # Other
        self.content_id: Optional[str] = None
        
        # Client reference
        self._client: Optional[AsyncClient] = None
        self._test_users: Optional[Dict[str, Any]] = None
    
    async def setup(self, client: AsyncClient, test_users: Dict[str, Any]):
        """
        Setup tất cả tokens và IDs cần thiết.
        Gọi một lần ở đầu test session hoặc test class.
        
        Args:
            client: AsyncClient fixture
            test_users: test_users fixture từ conftest
        """
        self._client = client
        self._test_users = test_users
        
        # Lấy tokens bằng cách login thật
        await self._login_all_users()
        
        # Lấy user IDs
        self._extract_user_ids()
    
    async def _login_all_users(self):
        """Login tất cả users và lưu tokens."""
        # Login admin
        self.admin_token = await self._login_user("admin")
        
        # Login instructors
        self.instructor1_token = await self._login_user("instructor1")
        self.instructor2_token = await self._login_user("instructor2")
        
        # Login students
        self.student1_token = await self._login_user("student1")
        self.student2_token = await self._login_user("student2")
        if "student3" in self._test_users:
            self.student3_token = await self._login_user("student3")
    
    async def _login_user(self, user_key: str) -> str:
        """
        Login một user và trả về token.
        
        Args:
            user_key: Key của user trong test_users dict
            
        Returns:
            str: Access token
        """
        login_payload = {
            "email": self._test_users[user_key]["email"],
            "password": self._test_users[user_key]["password"],
            "remember_me": False
        }
        response = await self._client.post("/api/v1/auth/login", json=login_payload)
        assert response.status_code == 200, f"Login failed for {user_key}: {response.json()}"
        return response.json()["access_token"]
    
    def _extract_user_ids(self):
        """Lấy user IDs từ test_users fixture."""
        self.admin_user_id = self._test_users["admin"]["id"]
        self.instructor1_user_id = self._test_users["instructor1"]["id"]
        self.instructor2_user_id = self._test_users["instructor2"]["id"]
        self.student1_user_id = self._test_users["student1"]["id"]
        self.student2_user_id = self._test_users["student2"]["id"]
    
    def get_headers(self, role: str = "student1") -> Dict[str, str]:
        """
        Lấy authorization headers cho một role.
        
        Args:
            role: "admin", "instructor1", "instructor2", "student1", "student2", etc.
            
        Returns:
            Dict với Authorization header
        """
        token_map = {
            "admin": self.admin_token,
            "instructor1": self.instructor1_token,
            "instructor2": self.instructor2_token,
            "student1": self.student1_token,
            "student2": self.student2_token,
            "student3": self.student3_token,
        }
        
        token = token_map.get(role)
        if not token:
            raise ValueError(f"Token not found for role: {role}")
        
        return {"Authorization": f"Bearer {token}"}
    
    def get_token(self, role: str = "student1") -> str:
        """
        Lấy token cho một role.
        
        Args:
            role: "admin", "instructor1", "instructor2", "student1", "student2", etc.
            
        Returns:
            str: Access token
        """
        token_map = {
            "admin": self.admin_token,
            "instructor1": self.instructor1_token,
            "instructor2": self.instructor2_token,
            "student1": self.student1_token,
            "student2": self.student2_token,
            "student3": self.student3_token,
        }
        
        token = token_map.get(role)
        if not token:
            raise ValueError(f"Token not found for role: {role}")
        
        return token
    
    def set(self, key: str, value: Any):
        """
        Set một biến động.
        
        Args:
            key: Tên biến
            value: Giá trị
        """
        setattr(self, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get một biến động.
        
        Args:
            key: Tên biến
            default: Giá trị mặc định nếu không tìm thấy
            
        Returns:
            Giá trị của biến
        """
        return getattr(self, key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Export tất cả variables thành dict.
        Hữu ích cho debugging.
        
        Returns:
            Dict chứa tất cả variables
        """
        return {
            "tokens": {
                "admin": self.admin_token,
                "instructor1": self.instructor1_token,
                "instructor2": self.instructor2_token,
                "student1": self.student1_token,
                "student2": self.student2_token,
            },
            "user_ids": {
                "admin": self.admin_user_id,
                "instructor1": self.instructor1_user_id,
                "instructor2": self.instructor2_user_id,
                "student1": self.student1_user_id,
                "student2": self.student2_user_id,
            },
            "resources": {
                "course_id": self.course_id,
                "module_id": self.module_id,
                "lesson_id": self.lesson_id,
                "quiz_id": self.quiz_id,
                "enrollment_id": self.enrollment_id,
                "class_id": self.class_id,
                "conversation_id": self.conversation_id,
            }
        }
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<TestVariables: {len([k for k, v in self.__dict__.items() if v is not None])} variables set>"


# Global instance (optional - có thể dùng hoặc không)
test_vars = TestVariables()
