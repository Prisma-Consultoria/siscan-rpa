from src.siscan.utils.schema_validator import SchemaValidator
from pathlib import Path

from src.env import SISCAN_URL, SISCAN_USER, SISCAN_PASSWORD
from dotenv import load_dotenv
import logging

from src.siscan.requisicao_exame_mamografia import RequisicaoExameMamografia

logger = logging.getLogger(__name__)


# python -m src.siscan.scrapping
def main():
    current_path = Path(__file__).resolve()
    root_path = current_path.parent.parent
    env_path = root_path / ".env"
    load_dotenv(dotenv_path=env_path)

    requisicao = RequisicaoExameMamografia(
        url_base=SISCAN_URL,
        user=SISCAN_USER,
        password=SISCAN_PASSWORD,
    )

    fake_path = root_path / "fake_data.json"
    if fake_path.exists():
        dados_path = fake_path
    else:
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
