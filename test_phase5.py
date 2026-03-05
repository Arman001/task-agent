import unittest
from state import AgentState
from agent import agent
import uuid
from preference_manager import preference_manager

class TestPhase5Approvals(unittest.TestCase):
    def setUp(self):
        # Reset preferences to ensure a clean slate
        preference_manager.reset_preferences()
        self.session_id = str(uuid.uuid4())

    def _create_state(self, task: str) -> AgentState:
        return AgentState(
            task=task,
            complexity="",
            plan=[],
            current_step=0,
            step_results=[],
            result="",
            messages=[],
            errors=[],
            retry_count=0,
            max_retries=1,
            tool_status={},
            fallback_triggered=False,
            session_id=self.session_id,
            memory_context={},
            should_save_memory=False, # don't pollute memory db
            pending_approval={},
            approval_granted=False,
            approval_history=[],
            user_preferences={},
            risk_level="SAFE",
            skip_current_step=False
        )

    def test_safe_auto_executes(self):
        state = self._create_state("Calculate 50 * 20")
        result_state = agent.invoke(state)
        # Verify it went through and succeeded
        self.assertIn("1000", result_state.get('result', ''))
        # No actual assertion needed on prompt since we can't easily mock input,
        # but if it prompts, the test would block (which will fail the test runner or timeout)
        
    def test_preferences_update(self):
        # file_write is AUTO by default, let's set it to NEVER_ASK
        preference_manager.set_preference("file_write", "NEVER_ASK")
        self.assertEqual(preference_manager.get_preference("file_write"), "NEVER_ASK")

if __name__ == '__main__':
    unittest.main()
