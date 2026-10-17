"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import (
    load_yaml,
    check_env_vars,
    print_section_header,
    validate_prompt_structure,
)

load_dotenv()

PROMPT_NAME = "bug_to_user_story_v2"
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / f"{PROMPT_NAME}.yml"


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        for error in errors:
            print(f"Erro de validacao: {error}", file=sys.stderr)
        return False

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return False

    try:
        messages = [("system", prompt_data["system_prompt"])]
        if prompt_data.get("user_prompt"):
            messages.append(("human", prompt_data["user_prompt"]))
        prompt = ChatPromptTemplate.from_messages(messages)
        prompt.metadata = {
            key: value
            for key, value in prompt_data.items()
            if key not in ("system_prompt", "user_prompt")
        }
        tags = list(dict.fromkeys(
            prompt_data.get("tags", []) + prompt_data["techniques_applied"]
        ))
        username = os.environ["USERNAME_LANGSMITH_HUB"].strip()
        url = hub.push(
            f"{username}/{prompt_name}",
            prompt,
            api_key=os.environ["LANGSMITH_API_KEY"],
            api_url=os.getenv("LANGSMITH_ENDPOINT") or None,
            new_repo_is_public=True,
            new_repo_description=prompt_data["description"],
            tags=tags,
        )
        print(f"Prompt publicado: {url}")
        return True
    except Exception as error:
        print(f"Erro ao publicar prompt: {error}", file=sys.stderr)
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    if not isinstance(prompt_data, dict):
        return False, ["O prompt deve ser um mapeamento YAML."]

    errors = []
    for field in ("description", "system_prompt", "version"):
        value = prompt_data.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} deve ser um texto nao vazio.")
    if "user_prompt" in prompt_data and not isinstance(prompt_data["user_prompt"], str):
        errors.append("user_prompt deve ser um texto.")
    for field in ("tags", "techniques_applied"):
        values = prompt_data.get(field, [])
        if not isinstance(values, list) or any(
            not isinstance(value, str) or not value.strip() for value in values
        ):
            errors.append(f"{field} deve ser uma lista de textos nao vazios.")
    if errors:
        return False, errors
    return validate_prompt_structure(prompt_data)


def main():
    """Função principal"""
    print_section_header(f"Publicar prompt: {PROMPT_NAME}")
    prompts = load_yaml(str(PROMPT_PATH))
    if not isinstance(prompts, dict):
        print("Erro: arquivo de prompts ausente ou invalido.", file=sys.stderr)
        return 1
    if PROMPT_NAME not in prompts:
        print(f"Erro: o YAML deve conter a chave {PROMPT_NAME}.", file=sys.stderr)
        return 1
    prompt_data = prompts[PROMPT_NAME]
    if isinstance(prompt_data, dict) and prompt_data.get("version") != "v2":
        print("Erro: a versao do prompt deve ser v2.", file=sys.stderr)
        return 1
    return 0 if push_prompt_to_langsmith(PROMPT_NAME, prompt_data) else 1


if __name__ == "__main__":
    sys.exit(main())
