from threading import Lock

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


scan_store = InMemoryScanStore()
