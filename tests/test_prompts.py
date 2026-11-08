"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import re
import unicodedata
from pathlib import Path

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_NAME = "bug_to_user_story_v2"

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class TestPrompts:
    @pytest.fixture
    def prompt_data(self):
        prompts = load_prompts(PROMPT_FILE)
        assert isinstance(prompts, dict)
        assert PROMPT_NAME in prompts
        return prompts[PROMPT_NAME]

    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert isinstance(prompt_data.get("system_prompt"), str)
        assert prompt_data["system_prompt"].strip()

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system_prompt = unicodedata.normalize(
            "NFKD", prompt_data["system_prompt"]
        ).encode("ascii", "ignore").decode("ascii").casefold()
        assert re.search(r"\bvoce\s+e\b", system_prompt)
        assert "product manager" in system_prompt

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data["system_prompt"].casefold()
        uses_user_story_format = (
            "user story:" in system_prompt
            and "criterios de aceitacao:" in system_prompt
        )
        assert "markdown" in system_prompt or uses_user_story_format

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_data["system_prompt"]
        assert re.search(r"\bExemplo\s+\d+\s*:", system_prompt, re.IGNORECASE)
        assert re.search(r"\bRelato\s*:", system_prompt, re.IGNORECASE)
        assert re.search(r"\bResposta\s*:", system_prompt, re.IGNORECASE)

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        prompt_text = yaml.safe_dump(prompt_data, allow_unicode=True).casefold()
        assert "[todo]" not in prompt_text

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_data.get("techniques_applied")
        assert isinstance(techniques, list)
        assert len(techniques) >= 2
        assert all(isinstance(technique, str) and technique.strip() for technique in techniques)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])