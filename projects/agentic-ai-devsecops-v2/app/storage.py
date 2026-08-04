import httpx
from threading import Lock

from app.config import settings
from app.models import ActionRoute, ScanResponse


class InMemoryScanStore:
    def __init__(self) -> None:
        self._scans: dict[str, ScanResponse] = {}
        self._lock = Lock()

    def save(self, scan: ScanResponse) -> None:
        with self._lock:
            self._scans[scan.scan_id] = scan

    def get(self, scan_id: str) -> ScanResponse | None:
        with self._lock:
            return self._scans.get(scan_id)

    def list_review_queue(self) -> list[ScanResponse]:
        with self._lock:
            return [
                scan
                for scan in self._scans.values()
                if any(finding.route == ActionRoute.human_review for finding in scan.findings)
            ]


class SupabaseScanStore:
    def __init__(self) -> None:
        self._url = settings.supabase_url.rstrip("/") if settings.supabase_url else ""
        self._key = settings.supabase_service_role_key or settings.supabase_anon_key
        self._headers = {
            "apikey": self._key,
            "Authorization": f"Bearer {self._key}",
            "Content-Type": "application/json",
            # Required by PostgREST to update an existing scan_id when the
            # webhook is retried or a queued scan is replaced by its result.
            "Prefer": "resolution=merge-duplicates",
        }

    def save(self, scan: ScanResponse) -> None:
        if not self._url or not self._key:
            raise RuntimeError("Supabase storage is not configured")

        payload = {
            "scan_id": scan.scan_id,
            "payload": scan.model_dump(mode="json"),
            "review_required": any(finding.route == ActionRoute.human_review for finding in scan.findings),
        }
        response = httpx.post(
            f"{self._url}/rest/v1/scans?on_conflict=scan_id",
            headers=self._headers,
            json=payload,
            timeout=10,
        )
        response.raise_for_status()

    def get(self, scan_id: str) -> ScanResponse | None:
        if not self._url or not self._key:
            raise RuntimeError("Supabase storage is not configured")

        response = httpx.get(
            f"{self._url}/rest/v1/scans",
            headers=self._headers,
            params={"select": "payload", "scan_id": f"eq.{scan_id}"},
            timeout=10,
        )
        response.raise_for_status()
        rows = response.json()
        if not rows:
            return None
        return ScanResponse.model_validate(rows[0]["payload"])

    def list_review_queue(self) -> list[ScanResponse]:
        if not self._url or not self._key:
            raise RuntimeError("Supabase storage is not configured")

        response = httpx.get(
            f"{self._url}/rest/v1/scans",
            headers=self._headers,
            params={"select": "payload"},
            timeout=10,
        )
        response.raise_for_status()
        rows = response.json()
        scans: list[ScanResponse] = []
        for row in rows:
            scan = ScanResponse.model_validate(row["payload"])
            if any(finding.route == ActionRoute.human_review for finding in scan.findings):
                scans.append(scan)
        return scans


class StorageRouter:
    def __init__(self) -> None:
        if settings.storage_backend.lower() == "supabase":
            self._backend: InMemoryScanStore | SupabaseScanStore = SupabaseScanStore()
        else:
            self._backend = InMemoryScanStore()

    def save(self, scan: ScanResponse) -> None:
        self._backend.save(scan)

    def get(self, scan_id: str) -> ScanResponse | None:
        return self._backend.get(scan_id)

    def list_review_queue(self) -> list[ScanResponse]:
        return self._backend.list_review_queue()


scan_store = StorageRouter()
