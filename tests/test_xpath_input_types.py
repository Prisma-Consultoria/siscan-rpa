import pytest
import pytest_asyncio
from src.siscan.requisicao_exame_mamografia import RequisicaoExameMamografia
from src.utils.xpath_constructor import XPathConstructor as XPE, InputType
from src.utils.validator import Validator
from src.siscan.context import SiscanBrowserContext
from src.env import SISCAN_URL, SISCAN_USER, SISCAN_PASSWORD

import logging

logger = logging.getLogger(__name__)


@pytest_asyncio.fixture(scope="session")
async def siscan_form():
    """Autentica no SIScan e navega até o formulário de novo exame."""
    req = RequisicaoExameMamografia(
        base_url=SISCAN_URL,
        user=SISCAN_USER,
        password=SISCAN_PASSWORD,
    )
    req._context = SiscanBrowserContext(headless=True)

    await req.authenticate()
    await req._novo_exame(event_button=True)
    yield req

    await req.context.close()


def _load_data(path):
    return Validator.load_json(path)


@pytest.mark.asyncio(loop_scope="session")
async def test_fill_text_input(siscan_form, fake_json_file):
    data = _load_data(fake_json_file)
    xpath = await XPE.create(siscan_form.context)
    label = siscan_form.get_field_label("ponto_de_referencia")
    await xpath.find_form_input(label, InputType.TEXT)
    await xpath.handle_fill(data["ponto_de_referencia"], reset=False)
    text, value = await xpath.get_value(InputType.TEXT)
    assert value == data["ponto_de_referencia"]


@pytest.mark.asyncio(loop_scope="session")
async def test_fill_select_input(siscan_form, fake_json_file):
    data = _load_data(fake_json_file)
    xpath = await XPE.create(siscan_form.context)
    label = siscan_form.get_field_label("escolaridade")
    await xpath.find_form_input(label, InputType.SELECT)
    await xpath.handle_fill(data["escolaridade"], reset=False)
    text, value = await xpath.get_value(InputType.SELECT)
    assert value is not None
