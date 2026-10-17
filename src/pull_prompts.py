"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

"""

import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from utils import save_yaml

load_dotenv()

PROMPT_ID = "leonanluppi/bug_to_user_story_v1"
PROMPT_NAME = "bug_to_user_story_v1"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "prompts" / f"{PROMPT_NAME}.yml"


def pull_prompts_from_langsmith():
    """Baixa o prompt do Hub e salva os templates no formato YAML local."""
    prompt = hub.pull(PROMPT_ID)
    if isinstance(prompt, ChatPromptTemplate):
        system_prompt = "\n\n".join(
            message.prompt.template
            for message in prompt.messages
            if isinstance(message, SystemMessagePromptTemplate)
        )
        user_prompt = "\n\n".join(
            message.prompt.template
            for message in prompt.messages
            if isinstance(message, HumanMessagePromptTemplate)
        )
    elif isinstance(prompt, PromptTemplate):
        system_prompt = prompt.template
        user_prompt = ""
    else:
        raise ValueError(f"Tipo de prompt nao suportado: {type(prompt).__name__}")

    prompt_data = {
        PROMPT_NAME: {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
        }
    }
    if not save_yaml(prompt_data, str(OUTPUT_PATH)):
        raise OSError(f"Nao foi possivel salvar o prompt em {OUTPUT_PATH}")
    print(f"Prompt {PROMPT_ID} salvo em {OUTPUT_PATH}")


def main():
    """Função principal"""
    try:
        pull_prompts_from_langsmith()
    except Exception as error:
        print(f"Erro ao baixar prompt: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
