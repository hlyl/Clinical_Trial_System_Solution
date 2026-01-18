"""API client for communicating with CTSR backend."""

import os
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel


class APIClient:
    """Client for CTSR API communication."""

    def __init__(self, base_url: str = "http://localhost:8001"):
        """Initialize API client.

        Args:
            base_url: Base URL for API endpoints
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = 30.0

    def _get_headers(self, user_email: str = "dev@localhost") -> Dict[str, str]:
        """Get request headers with auth."""
        return {
            "Content-Type": "application/json",
            "User-Email": user_email,
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        user_email: str = "dev@localhost",
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Make HTTP request to API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            user_email: User email for auth
            params: Query parameters
            json_data: JSON body data

        Returns:
            Response JSON or None if error
        """
        try:
            url = f"{self.base_url}{endpoint}"
            headers = self._get_headers(user_email)

            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json=json_data,
                )
                response.raise_for_status()
                return response.json() if response.content else None
        except httpx.HTTPError as e:
            print(f"API Error: {e}")
            return None

    # Health & Status
    def get_health(self) -> Optional[Dict[str, Any]]:
        """Get API health status."""
        return self._make_request("GET", "/health")

    # Lookups
    def get_lookups(self) -> Optional[Dict[str, Any]]:
        """Get all reference/lookup data."""
        return self._make_request("GET", "/api/v1/lookups")

    # Vendors
    def list_vendors(
        self,
        vendor_type: Optional[str] = None,
        is_active: bool = True,
        limit: int = 50,
        offset: int = 0,
        user_email: str = "dev@localhost",
    ) -> Optional[Dict[str, Any]]:
        """List vendors with filtering and pagination."""
        params = {
            "is_active": is_active,
            "limit": limit,
            "offset": offset,
        }
        if vendor_type:
            params["vendor_type"] = vendor_type

        return self._make_request(
            "GET",
            "/api/v1/vendors",
            user_email=user_email,
            params=params,
        )

    def get_vendor(self, vendor_id: str, user_email: str = "dev@localhost") -> Optional[Dict[str, Any]]:
        """Get vendor details."""
        return self._make_request(
            "GET",
            f"/api/v1/vendors/{vendor_id}",
            user_email=user_email,
        )

    def create_vendor(
        self,
        vendor_code: str,
        vendor_name: str,
        vendor_type: str,
        contact_name: Optional[str] = None,
        contact_email: Optional[str] = None,
        user_email: str = "dev@localhost",
    ) -> Optional[Dict[str, Any]]:
        """Create a new vendor."""
        return self._make_request(
            "POST",
            "/api/v1/vendors",
            user_email=user_email,
            json_data={
                "vendor_code": vendor_code,
                "vendor_name": vendor_name,
                "vendor_type": vendor_type,
                "contact_name": contact_name,
                "contact_email": contact_email,
            },
        )

    def update_vendor(
        self,
        vendor_id: str,
        vendor_name: Optional[str] = None,
        vendor_type: Optional[str] = None,
        contact_name: Optional[str] = None,
        contact_email: Optional[str] = None,
        is_active: Optional[bool] = None,
        user_email: str = "dev@localhost",
    ) -> Optional[Dict[str, Any]]:
        """Update vendor."""
        data = {}
        if vendor_name:
            data["vendor_name"] = vendor_name
        if vendor_type:
            data["vendor_type"] = vendor_type
        if contact_name is not None:
            data["contact_name"] = contact_name
        if contact_email is not None:
            data["contact_email"] = contact_email
        if is_active is not None:
            data["is_active"] = is_active

        return self._make_request(
            "PUT",
            f"/api/v1/vendors/{vendor_id}",
            user_email=user_email,
            json_data=data,
        )

    # Systems
    def list_systems(
        self,
        category_code: Optional[str] = None,
        validation_status: Optional[str] = None,
        is_active: bool = True,
        limit: int = 50,
        offset: int = 0,
        user_email: str = "dev@localhost",
    ) -> Optional[Dict[str, Any]]:
        """List system instances with filtering and pagination."""
        params = {
            "is_active": is_active,
            "limit": limit,
            "offset": offset,
        }
        if category_code:
            params["category_code"] = category_code
        if validation_status:
            params["validation_status_code"] = validation_status

        return self._make_request(
            "GET",
            "/api/v1/systems",
            user_email=user_email,
            params=params,
        )

    def get_system(self, system_id: str, user_email: str = "dev@localhost") -> Optional[Dict[str, Any]]:
        """Get system instance details."""
        return self._make_request(
            "GET",
            f"/api/v1/systems/{system_id}",
            user_email=user_email,
        )

    def create_system(
        self,
        instance_code: str,
        category_code: str,
        platform_name: str,
        validation_status_code: str,
        platform_vendor_id: Optional[str] = None,
        user_email: str = "dev@localhost",
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """Create a new system instance."""
        data = {
            "instance_code": instance_code,
            "category_code": category_code,
            "platform_name": platform_name,
            "validation_status_code": validation_status_code,
        }
        if platform_vendor_id:
            data["platform_vendor_id"] = platform_vendor_id
        data.update(kwargs)

        return self._make_request(
            "POST",
            "/api/v1/systems",
            user_email=user_email,
            json_data=data,
        )

    def update_system(
        self,
        system_id: str,
        instance_code: Optional[str] = None,
        platform_name: Optional[str] = None,
        category_code: Optional[str] = None,
        validation_status_code: Optional[str] = None,
        is_active: Optional[bool] = None,
        user_email: str = "dev@localhost",
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """Update system instance."""
        data = {}
        if instance_code:
            data["instance_code"] = instance_code
        if platform_name:
            data["platform_name"] = platform_name
        if category_code:
            data["category_code"] = category_code
        if validation_status_code:
            data["validation_status_code"] = validation_status_code
        if is_active is not None:
            data["is_active"] = is_active
        data.update(kwargs)

        return self._make_request(
            "PUT",
            f"/api/v1/systems/{system_id}",
            user_email=user_email,
            json_data=data,
        )

    # Trials
    def list_trials(
        self,
        trial_status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        user_email: str = "dev@localhost",
    ) -> Optional[Dict[str, Any]]:
        """List trials with filtering and pagination."""
        params = {
            "limit": limit,
            "offset": offset,
        }
        if trial_status:
            params["trial_status"] = trial_status

        return self._make_request(
            "GET",
            "/api/v1/trials",
            user_email=user_email,
            params=params,
        )

    def get_trial(self, trial_id: str, user_email: str = "dev@localhost") -> Optional[Dict[str, Any]]:
        """Get trial details."""
        return self._make_request(
            "GET",
            f"/api/v1/trials/{trial_id}",
            user_email=user_email,
        )

    def create_trial(
        self,
        protocol_number: str,
        trial_title: str,
        trial_status: str = "PLANNED",
        user_email: str = "dev@localhost",
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """Create a new trial."""
        data = {
            "protocol_number": protocol_number,
            "trial_title": trial_title,
            "trial_status": trial_status,
        }
        data.update(kwargs)

        return self._make_request(
            "POST",
            "/api/v1/trials",
            user_email=user_email,
            json_data=data,
        )

    def update_trial(
        self,
        trial_id: str,
        protocol_number: Optional[str] = None,
        trial_title: Optional[str] = None,
        trial_status: Optional[str] = None,
        is_active: Optional[bool] = None,
        user_email: str = "dev@localhost",
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """Update trial."""
        data = {}
        if protocol_number:
            data["protocol_number"] = protocol_number
        if trial_title:
            data["trial_title"] = trial_title
        if trial_status:
            data["trial_status"] = trial_status
        if is_active is not None:
            data["is_active"] = is_active
        data.update(kwargs)

        return self._make_request(
            "PUT",
            f"/api/v1/trials/{trial_id}",
            user_email=user_email,
            json_data=data,
        )

    # Trial Systems
    def link_system_to_trial(
        self,
        trial_id: str,
        system_id: str,
        criticality_code: str,
        user_email: str = "dev@localhost",
    ) -> Optional[Dict[str, Any]]:
        """Link a system to a trial."""
        return self._make_request(
            "POST",
            f"/api/v1/trials/{trial_id}/systems",
            user_email=user_email,
            json_data={
                "instance_id": system_id,
                "criticality_code": criticality_code,
            },
        )

    def get_trial_systems(
        self,
        trial_id: str,
        user_email: str = "dev@localhost",
    ) -> Optional[Dict[str, Any]]:
        """Get systems linked to a trial."""
        return self._make_request(
            "GET",
            f"/api/v1/trials/{trial_id}/systems",
            user_email=user_email,
        )

    # Confirmations
    def list_confirmations(
        self,
        confirmation_status: Optional[str] = None,
        confirmation_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        user_email: str = "dev@localhost",
    ) -> Optional[Dict[str, Any]]:
        """List confirmations with filtering and pagination."""
        params = {
            "limit": limit,
            "offset": offset,
        }
        if confirmation_status:
            params["confirmation_status"] = confirmation_status
        if confirmation_type:
            params["confirmation_type"] = confirmation_type

        return self._make_request(
            "GET",
            "/api/v1/confirmations",
            user_email=user_email,
            params=params,
        )

    def get_confirmation(
        self,
        confirmation_id: str,
        user_email: str = "dev@localhost",
    ) -> Optional[Dict[str, Any]]:
        """Get confirmation details."""
        return self._make_request(
            "GET",
            f"/api/v1/confirmations/{confirmation_id}",
            user_email=user_email,
        )

    def create_confirmation(
        self,
        confirmation_type: str,
        trial_id: str,
        system_id: str,
        confirmation_status: str = "PENDING",
        user_email: str = "dev@localhost",
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """Create a new confirmation."""
        data = {
            "confirmation_type": confirmation_type,
            "trial_id": trial_id,
            "system_id": system_id,
            "confirmation_status": confirmation_status,
        }
        data.update(kwargs)

        return self._make_request(
            "POST",
            "/api/v1/confirmations",
            user_email=user_email,
            json_data=data,
        )

    def update_confirmation(
        self,
        confirmation_id: str,
        confirmation_status: Optional[str] = None,
        user_email: str = "dev@localhost",
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """Update confirmation."""
        data = {}
        if confirmation_status:
            data["confirmation_status"] = confirmation_status
        data.update(kwargs)

        return self._make_request(
            "PUT",
            f"/api/v1/confirmations/{confirmation_id}",
            user_email=user_email,
            json_data=data,
        )

    # Admin
    def get_admin_stats(
        self,
        user_email: str = "dev@localhost",
    ) -> Optional[Dict[str, Any]]:
        """Get admin dashboard statistics."""
        return self._make_request(
            "GET",
            "/api/v1/admin/dashboard",
            user_email=user_email,
        )


# Global API client instance
api_client = APIClient(base_url=os.getenv("API_BASE_URL", "http://localhost:8001"))
