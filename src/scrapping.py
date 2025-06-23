from src.siscan.utils.validator import Validator
from pathlib import Path
import asyncio
from src.env import SISCAN_URL, SISCAN_USER, SISCAN_PASSWORD
import logging

from src.siscan.requisicao_exame_mamografia import RequisicaoExameMamografia

logger = logging.getLogger(__name__)


# python -m src.siscan.scrapping
async def main():
    current_path = Path(__file__).resolve()
    root_path = current_path.parent.parent

    requisicao = RequisicaoExameMamografia(
        url_base=SISCAN_URL,
        user=SISCAN_USER,
        password=SISCAN_PASSWORD,
    )

    data_path = root_path / "fake_data.json"

    dados = Validator.load_json(data_path)

    # requisicao.buscar_cartao_sus(dados)

    await asyncio.to_thread(requisicao.preencher, dados)

    informations = requisicao.context.information_messages
    if informations:
        logger.info("Mensagens informativas coletadas:")
        for key, messages in informations.items():
            logger.info(f"{key}: {', '.join(messages)}")
    else:
        logger.info("Nenhuma mensagem informativa encontrada.")

    requisicao.context.close()

if __name__ == "__main__":
    asyncio.run(main())
