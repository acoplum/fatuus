import os
import unittest

os.environ.setdefault("GOOGLE_API_KEY", "test-key-for-unit-tests")

from agno.models.google import Gemini

from fatuus.agents import (
    build_anti_simetria_agent,
    build_cadencia_agent,
    build_integridade_agent,
    build_watermark_agent,
)


class TestAgentFactories(unittest.TestCase):
    def setUp(self):
        self.model = Gemini(id="gemini-3.7-flash")

    def test_cadencia_agent_has_pt_instructions(self):
        agent = build_cadencia_agent(self.model, lang="pt")
        self.assertIn("ritmo", agent.instructions.lower())

    def test_cadencia_agent_has_en_instructions(self):
        agent = build_cadencia_agent(self.model, lang="en")
        self.assertIn("rhythm", agent.instructions.lower())

    def test_anti_simetria_agent_built(self):
        agent = build_anti_simetria_agent(self.model, lang="pt")
        self.assertIn("paralelismos", agent.instructions.lower())

    def test_integridade_agent_built(self):
        agent = build_integridade_agent(self.model, lang="pt")
        self.assertIn("fato", agent.instructions.lower())

    def test_watermark_agent_built(self):
        agent = build_watermark_agent(self.model, lang="en")
        self.assertIn("watermark", agent.instructions.lower())


if __name__ == "__main__":
    unittest.main()
