import pytest
from src.siscan.requisicao_exame_mamografia import RequisicaoExameMamografia
from src.utils.xpath_constructor import XPathConstructor, InputType
from src.utils.validator import Validator
from src.env import SISCAN_URL, SISCAN_USER, SISCAN_PASSWORD


@pytest.fixture(scope="session")
def siscan_form():
    """Autentica no SIScan e navega até o formulário de novo exame."""
    req = RequisicaoExameMamografia(
        url_base=SISCAN_URL,
        user=SISCAN_USER,
        password=SISCAN_PASSWORD,
    )
    req.authenticate()
    req._novo_exame(event_button=True)
    yield req
    req.context.close()


def _load_data(path):
    return Validator.load_json(path)


def test_fill_text_input(siscan_form, fake_json_file):
    data = _load_data(fake_json_file)
    xpath = XPathConstructor(siscan_form.context)
    label = siscan_form.get_field_label("nome")
    await xpath.find_form_input(label, InputType.TEXT).handle_fill(data["nome"], reset=False)
    text, value = xpath.get_value(InputType.TEXT)
    assert value == data["nome"]


def test_fill_select_input(siscan_form, fake_json_file):
    data = _load_data(fake_json_file)
    xpath = XPathConstructor(siscan_form.context)
    label = siscan_form.get_field_label("nacionalidade")
    await xpath.find_form_input(label, InputType.SELECT).handle_fill(data["nacionalidade"], reset=False)
    text, value = xpath.get_value(InputType.SELECT)
    assert value is not None


def test_fill_date_input(siscan_form, fake_json_file):
    data = _load_data(fake_json_file)
    xpath = XPathConstructor(siscan_form.context)
    label = siscan_form.get_field_label("data_de_nascimento")
    await xpath.find_form_input(label, InputType.DATE).handle_fill(data["data_de_nascimento"], reset=False)
    text, value = xpath.get_value(InputType.DATE)
    assert value == data["data_de_nascimento"]


def test_fill_checkbox_input(siscan_form, fake_json_file):
    data = _load_data(fake_json_file)
    xpath = XPathConstructor(siscan_form.context)
    label = siscan_form.get_field_label("tem_nodulo_ou_caroco_na_mama")
    valores = data["tem_nodulo_ou_caroco_na_mama"]
    await xpath.find_form_input(label, InputType.CHECKBOX).handle_fill(valores, reset=False)
    result = xpath.get_value(InputType.CHECKBOX)
    assert isinstance(result, list)
    assert len(result) == len(valores)
