from __future__ import annotations


import os
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional


import requests




@dataclass
class SimpleResponse:
   status_code: int
   _json_data: Dict[str, Any]


   def json(self) -> Dict[str, Any]:
       return self._json_data




class FakeObjectApi:
   """
   Minimal in-memory API to make BDD tests deterministic and offline-friendly.
   Mirrors the behaviors asserted in the feature files (200/404/4xx).
   """


   def __init__(self) -> None:
       self._store: Dict[str, Dict[str, Any]] = {}


   def post(self, payload: Dict[str, Any]) -> SimpleResponse:
       name = payload.get("name")
       if not name:
           return SimpleResponse(400, {"error": "invalid payload"})


       object_id = uuid.uuid4().hex
       obj = {"id": object_id, **payload}
       self._store[object_id] = obj
       return SimpleResponse(200, obj)


   def get(self, object_id: str) -> SimpleResponse:
       obj = self._store.get(object_id)
       if not obj:
           return SimpleResponse(404, {"error": "not found"})
       return SimpleResponse(200, obj)


   def put(self, object_id: str, payload: Dict[str, Any]) -> SimpleResponse:
       if object_id not in self._store:
           return SimpleResponse(404, {"error": "not found"})
       obj = {"id": object_id, **payload}
       self._store[object_id] = obj
       return SimpleResponse(200, obj)


   def delete(self, object_id: str) -> SimpleResponse:
       if object_id not in self._store:
           return SimpleResponse(404, {"error": "not found"})
       del self._store[object_id]
       return SimpleResponse(200, {"deleted": True})




class ObjectApi:
   """
   Backend selector.
   - Default: fake in-memory API (no network)
   - Set LIVE_API=1 to hit the public endpoint
   """


   def __init__(self, base_url: str) -> None:
       self._base_url = base_url
       self._fake = FakeObjectApi()


   @property
   def live(self) -> bool:
       return os.getenv("LIVE_API", "").strip().lower() in {"1", "true", "yes", "y"}


   def post(self, payload: Dict[str, Any]):
       if not self.live:
           return self._fake.post(payload)
       return requests.post(self._base_url, json=payload, timeout=15)


   def get(self, object_id: str):
       if not self.live:
           return self._fake.get(object_id)
       return requests.get(f"{self._base_url}/{object_id}", timeout=15)


   def put(self, object_id: str, payload: Dict[str, Any]):
       if not self.live:
           return self._fake.put(object_id, payload)
       return requests.put(f"{self._base_url}/{object_id}", json=payload, timeout=15)


   def delete(self, object_id: str):
       if not self.live:
           return self._fake.delete(object_id)
       return requests.delete(f"{self._base_url}/{object_id}", timeout=15)









