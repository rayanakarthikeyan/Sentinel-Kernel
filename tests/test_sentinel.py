import os
import sys
import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock

from sentinel.sandbox.local_process import ProcessIsolatedSandbox
from sentinel.schemas.incident import TelemetryAlert, IncidentStatus
from sentinel.agent.orchestrator import SREOrchestrator

class TestSentinelKernel(unittest.TestCase):
    def setUp(self):
        self.sandbox = ProcessIsolatedSandbox()

    def tearDown(self):
        self.sandbox.cleanup()

    def test_sandbox_write_and_run(self):
        self.sandbox.initialize_workspace()
        self.sandbox.write_file("hello.py", "print('Sentinel Active')")
        result = self.sandbox.run_command("python hello.py")
        self.assertTrue(result.passed)
        self.assertIn("Sentinel Active", result.output)

    def test_remediation_pipeline(self):
        orchestrator = SREOrchestrator()
        alert = TelemetryAlert(
            alert_id="TEST-099",
            service_name="auth-core",
            error_name="TokenValidationDeadlock",
            message="Database pool exhaustion causing auth gateway timeout.",
            stack_trace='File "auth_service.py", line 89, in handle_request'
        )
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, 'auth_service.py').write_text(
                'def handle_request(payload):\n    return {"status": "failure"}\n')
            incident = orchestrator.remediate(alert, source_repo_path=folder)
        self.assertEqual(incident.status, IncidentStatus.RESOLVED)
        self.assertIsNotNone(incident.proposed_diff)
        self.assertTrue(incident.verification_result.passed)
        self.assertIn("Incident Post-Mortem", incident.post_mortem_markdown)

class ReproductionGateTests(unittest.TestCase):
    def test_missing_source_escalates_without_patch(self):
        alert = TelemetryAlert(alert_id='missing', service_name='test',
                              error_name='Error', message='No source supplied')
        result = SREOrchestrator().remediate(alert)
        self.assertEqual(result.status, IncidentStatus.ESCALATED)
        self.assertIsNone(result.proposed_diff)

    def test_already_passing_test_does_not_authorize_patch(self):
        alert = TelemetryAlert(alert_id='passing', service_name='test',
                              error_name='Error', message='Already passes')
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, 'service.py').write_text(
                'def handle_request(payload):\n    return {"status": "success"}\n')
            result = SREOrchestrator().remediate(alert, source_repo_path=folder)
        self.assertEqual(result.status, IncidentStatus.ESCALATED)
        self.assertIsNone(result.proposed_diff)

if __name__ == '__main__':
    unittest.main()
