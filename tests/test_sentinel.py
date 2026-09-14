import os
import sys
import unittest

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
        incident = orchestrator.remediate(alert)
        self.assertEqual(incident.status, IncidentStatus.RESOLVED)
        self.assertIsNotNone(incident.proposed_diff)
        self.assertTrue(incident.verification_result.passed)
        self.assertIn("Incident Post-Mortem", incident.post_mortem_markdown)

if __name__ == '__main__':
    unittest.main()
