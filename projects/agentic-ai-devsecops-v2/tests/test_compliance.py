import unittest

from app.agents.compliance import ComplianceCheckerAgent
from app.models import ScanRequest


class ComplianceCheckerAgentTests(unittest.IsolatedAsyncioTestCase):
    async def test_workflow_without_permissions_is_reported(self) -> None:
        request = ScanRequest(
            repository="example/repository",
            source_snapshot={
                ".github/workflows/ci.yml": "name: CI\non: push\n",
            },
        )

        findings = await ComplianceCheckerAgent().scan(request)

        permission_findings = [
            finding for finding in findings if finding.control == "GHA.PERM.1"
        ]
        self.assertEqual(len(permission_findings), 1)
        self.assertEqual(permission_findings[0].file_path, ".github/workflows/ci.yml")

    async def test_tekton_file_is_not_treated_as_github_actions_workflow(self) -> None:
        request = ScanRequest(
            repository="example/repository",
            source_snapshot={
                ".tekton/tasks.yml": "apiVersion: tekton.dev/v1beta1\nkind: Task\n",
            },
        )

        findings = await ComplianceCheckerAgent().scan(request)

        permission_findings = [
            finding for finding in findings if finding.control == "GHA.PERM.1"
        ]
        self.assertEqual(permission_findings, [])
