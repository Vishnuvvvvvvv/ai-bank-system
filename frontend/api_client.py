from __future__ import annotations

from typing import Any

import requests


class BankingApiError(Exception):
    pass


class BankingApiClient:
    def __init__(self, base_url: str, token: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.token = token

    @property
    def headers(self) -> dict[str, str]:
        if not self.token:
            return {}

        return {
            "Authorization": f"Bearer {self.token}",
        }

    def _handle_response(self, response: requests.Response) -> Any:
        try:
            payload = response.json()
        except ValueError:
            payload = response.text

        if response.status_code >= 400:
            message = payload.get("detail") if isinstance(payload, dict) else payload
            raise BankingApiError(str(message or "Banking API request failed"))

        return payload

    def login(self, email: str, password: str) -> str:
        response = requests.post(
            f"{self.base_url}/login",
            json={
                "email": email,
                "password": password,
            },
            timeout=30,
        )

        payload = self._handle_response(response)
        return payload["access_token"]

    def me(self) -> dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/me",
            headers=self.headers,
            timeout=30,
        )

        return self._handle_response(response)

    def balance(self) -> dict[str, Any] | None:
        response = requests.get(
            f"{self.base_url}/balance",
            headers=self.headers,
            timeout=30,
        )

        return self._handle_response(response)

    def transactions(self) -> list[dict[str, Any]]:
        response = requests.get(
            f"{self.base_url}/transactions",
            headers=self.headers,
            timeout=30,
        )

        return self._handle_response(response)

    def loans(self) -> list[dict[str, Any]]:
        response = requests.get(
            f"{self.base_url}/loans",
            headers=self.headers,
            timeout=30,
        )

        return self._handle_response(response)

    def loan_eligibility(self, loan_type: str) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/loan-eligibility",
            headers=self.headers,
            json={
                "loan_type": loan_type,
            },
            timeout=30,
        )

        return self._handle_response(response)

    def documents(self) -> list[dict[str, Any]]:
        response = requests.get(
            f"{self.base_url}/documents",
            headers=self.headers,
            timeout=30,
        )

        return self._handle_response(response)

    def upload_document(
        self,
        file_name: str,
        content: bytes,
        mime_type: str,
        document_type: str | None = None,
    ) -> dict[str, Any]:
        data = {}

        if document_type:
            data["document_type"] = document_type

        response = requests.post(
            f"{self.base_url}/documents/upload",
            headers=self.headers,
            data=data,
            files={
                "file": (
                    file_name,
                    content,
                    mime_type or "application/octet-stream",
                )
            },
            timeout=60,
        )

        return self._handle_response(response)

    def upload_documents(
        self,
        uploads: list[tuple[str, bytes, str | None]],
        document_type: str | None = None,
    ) -> dict[str, Any]:
        data = {}

        if document_type:
            data["document_type"] = document_type

        files = [
            (
                "files",
                (
                    file_name,
                    content,
                    mime_type or "application/octet-stream",
                ),
            )
            for file_name, content, mime_type in uploads
        ]

        response = requests.post(
            f"{self.base_url}/documents/upload-batch",
            headers=self.headers,
            data=data,
            files=files,
            timeout=120,
        )

        return self._handle_response(response)

    def chat(self, message: str, thread_id: str | None = None) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/chat",
            headers=self.headers,
            json={
                "message": message,
                "thread_id": thread_id,
            },
            timeout=120,
        )

        return self._handle_response(response)
