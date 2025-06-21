import logging

from src.siscan.utils.schema_validator import SchemaValidator

# Ativa o logging no nível DEBUG para todo o projeto
logging.basicConfig(
    level=logging.DEBUG,  # Troque para logging.INFO caso deseje menos verbosidade
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

from pathlib import Path

import os
from dotenv import load_dotenv

from src.siscan.requisicao_exame_mamografia import RequisicaoExameMamografia

logger = logging.getLogger(__name__)


# python -m src.siscan.scrapping
def main():
    current_path = Path(__file__).resolve()
    root_path = current_path.parent.parent
    env_path = root_path / ".env"
    load_dotenv(dotenv_path=env_path)

    requisicao = RequisicaoExameMamografia(
        url_base=os.getenv("SISCAN_URL", "https://siscan.saude.gov.br/"),
        user=os.getenv("SISCAN_USER", ""),
        password=os.getenv("SISCAN_PASSWORD", ""),
    )

    dados_path = Path(__file__).parent / "dados.json"
    dados = SchemaValidator.load_json(dados_path)

    # requisicao.buscar_cartao_sus(dados)

    requisicao.preencher(dados)

    informations = requisicao.context.information_messages
    if informations:
        logger.info("Mensagens informativas coletadas:")
        for key, messages in informations.items():
            logger.info(f"{key}: {', '.join(messages)}")
    else:
        logger.info("Nenhuma mensagem informativa encontrada.")

    requisicao.context.close()


if __name__ == "__main__":
    main()
