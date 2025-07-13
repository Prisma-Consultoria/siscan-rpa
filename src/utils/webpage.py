from pathlib import Path
from datetime import datetime
import logging
from abc import abstractmethod, ABC
from typing import Optional, Type, Any

from pydantic import BaseModel

from src.siscan.exception import FieldValueNotFoundError
from src.utils.SchemaMapExtractor import SchemaMapExtractor
from src.utils.xpath_constructor import XPathConstructor as XPE, InputType
from src.siscan.context import SiscanBrowserContext
from src.env import PRODUCTION


logger = logging.getLogger(__name__)


class WebPage(ABC):
    """
    Classe abstrata para navegação de páginas desde a página de origem e autenticação
    """

    FIELDS_MAP: dict[str, dict[str, Any]] = {}

    def __init__(
        self, base_url: str, user: str, password: str, schema_model: Type[BaseModel]
    ):
        self._base_url = base_url
        self._user = user
        self._password = password
        self._schema_model = schema_model
        self._context: Optional[SiscanBrowserContext] = None

    @property
    def context(self) -> SiscanBrowserContext:
        """
        Retorna o contexto Playwright associado a esta instância.
        """
        if self._context is None:
            self._initialize_context()
        return self._context

    def _initialize_context(self):
        self._context = SiscanBrowserContext(
            base_url=self._base_url,
            headless=not PRODUCTION,  # Para depuração, use False
            timeout=15000,
        )

    @abstractmethod
    async def _authenticate(self):
        raise NotImplementedError("Subclasses devem implementar este método.")

    @abstractmethod
    def get_map_label(self) -> dict[str, dict[str, Any]]:
        """Método abstrato para retornar o mapeamento de labels dos campos."""
        raise NotImplementedError("Subclasses devem implementar este método.")

    @abstractmethod
    def validation(self, data: dict):
        raise NotImplementedError("Subclasses devem implementar este método.")

    @property
    def schema_model(self) -> Type[BaseModel]:
        return self._schema_model

    def get_field_metadata(
        self, field_name: str, map_label: Optional[dict[str, tuple]] = None
    ) -> dict[str, str]:
        # Busca o valor no dicionário de mapeamento
        if map_label is None:
            map_data_label = self.get_map_label().get(field_name)
        else:
            map_data_label = map_label.get(field_name)

        if map_data_label is None:
            raise ValueError(f"get_field_metadata: Campo '{field_name}' não "
                             f"está mapeado.")

        if len(map_data_label) != 4:
            raise ValueError(f"get_field_metadata: Campo '{field_name}' "
                             f"mapeado incorretamente. Esperado 4 valores, "
                             f"recebido {len(map_data_label)}.")
        return map_data_label

    def get_field_label(
        self,
        field_name: str,
        map_label: Optional[dict[str, tuple[str, str, str, str]]] = None,
    ) -> str:
        """Retorna o texto do label associado ao campo, conforme o mapeamento."""
        if map_label is None:
            map_data_label = self.get_map_label().get(field_name)
        else:
            map_data_label = map_label.get(field_name)

        if map_data_label is None:
            raise ValueError(f"get_field_label: Campo '{field_name}' não está "
                             f"mapeado.")
        return map_data_label.get("label")

    def get_field_type(
        self,
        field_name: str,
        map_label: Optional[dict[str, tuple[str, str, str, str]]] = None,
    ) -> str:
        """Retorna o tipo do campo conforme definido no mapeamento."""
        if map_label is None:
            map_data_label = self.get_map_label().get(field_name)
        else:
            map_data_label = map_label.get(field_name)

        if map_data_label is None:
            raise ValueError(f"get_field_type: Campo '{field_name}' não está "
                             f"mapeado.")
        return map_data_label.get("input_type", "text")

    def get_field_required(
        self,
        field_name: str,
        map_label: Optional[dict[str, tuple[str, str, str, str]]] = None,
    ) -> bool:
        if map_label is None:
            map_data_label = self.get_map_label().get(field_name)
        else:
            map_data_label = map_label.get(field_name)

        if map_data_label is None:
            raise ValueError(f"get_field_required: Campo '{field_name}' não "
                             f"está mapeado.")
        return map_data_label.get("required", False)

    def get_field_xpath(
            self,
            field_name: str,
            map_label: Optional[dict[str, dict[str, Any]]] = None,
    ) -> str:
        """Retorna o xpath associado ao campo, conforme o mapeamento."""
        if map_label is None:
            map_data_label = self.get_map_label().get(field_name)
        else:
            map_data_label = map_label.get(field_name)
        if map_data_label is None:
            raise ValueError(
                f"get_field_xpath: Campo '{field_name}' não está mapeado.")
        return map_data_label.get("xpath", "")

    def get_field_value(self, field_name: str, data: dict) -> Optional[str | list]:
        """Retorna o valor do campo, convertendo via FIELDS_MAP se houver
        mapeamento; caso contrário, retorna o valor original."""
        value = data.get(field_name, None)

        if field_name in self.FIELDS_MAP.keys() and value is not None:
            # Mapeia o valor do campo para o valor específico definido no
            # mapeamento
            if isinstance(value, list):
                logger.warning(
                    f"O valor do campo '{field_name}' é uma lista ({value}). "
                    f"O mapeamento FIELDS_MAP espera um valor escalar. "
                    f"Ignorando o mapeamento e retornado o valor real "
                    f"fornecido em 'data'."
                )
            else:
                value = self.FIELDS_MAP[field_name].get(value, None)
        return value

    async def update_field_map_from_select(
        self,
        field_name: str,
        xpath: XPE,
        label_as_key: bool = True,
        timeout: int = 10,
    ) -> None:
        """
        Atualiza o dicionário FIELDS_MAP[field_name] com opções do select da
        página.

        Este método utiliza um XPathConstructor já posicionado no campo
        <select>, recupera todas as opções (value, texto) e as insere em
        FIELDS_MAP para permitir mapeamento automático no preenchimento do
        formulário.

        Parâmetros
        ----------
        field_name : str
            Nome do campo no dicionário FIELDS_MAP a ser atualizado.
        xpath : XPathConstructor
            Instância já posicionada no <select> desejado.
        label_as_key : bool, opcional
            Se True (padrão), usa o texto do option como chave do dicionário
            e o value como valor. Se False, inverte (útil para selects onde
            o backend exige a chave como value).
        timeout : int, opcional
            Tempo máximo para aguardar o <select> na página.

        Retorno
        -------
        None

        Exemplo
        -------
        ```python
        xpath.find_form_input("Unidade de Saúde", InputType.SELECT)
        self.update_field_map_from_select("unidade_saude", xpath)
        print(self.FIELDS_MAP["unidade_saude"])
        {'0015466 - CENTRO DE ...': '4', ...}
        ```
        """
        options = await xpath.get_select_options(timeout=timeout)
        if label_as_key:
            mapping = {label: value for value, label in options.items()}
        else:
            mapping = {value: label for value, label in options.items()}
        self.FIELDS_MAP[field_name] = mapping

        xpath.reset()

    def _mount_fields_map_and_data(
        self,
        data: dict,
        map_label: dict[str, tuple[str, str, str]],
        suffix: Optional[str] = ":",
    ) -> tuple[dict[str, tuple[str, str, str]], dict[str, str]]:
        """
        Gera o dicionário campos_map e o dicionário data_final para uso em
        preenchimento genérico de formulários.

        Parâmetros
        ----------
        data : dict
            Dicionário de dados originais (nomes de campos como chave).
        map_label : dict[str, tuple[str, str, str]]
            Dicionário com nomes de campos como chave e tuplas contendo
            (label, tipo de campo, requirement_level) como valor.
        suffix : str, opcional (default=":")

        Retorna
        -------
        tuple (campos_map, data_final)
            - campos_map: dict[str, tuple[str, str, str]]
            - data_final: dict[str, str]
        """
        if suffix is None:
            suffix = ""

        fields_map = {}
        data_final = {}
        for field_name in data.keys():
            if field_name not in map_label.keys():
                logger.warning(
                    f"Campo '{field_name}' não está mapeado ou não é editável. "
                    f"Ignorado."
                )
                continue
            field_metadata = self.get_field_metadata(
                field_name, map_label
            )
            fields_map[field_name] = SchemaMapExtractor.make_field_dict(
                f"{field_metadata.get('label')}{suffix}",
                field_metadata.get("input_type", 'text'),
                field_metadata.get("required", False),
                field_metadata.get("xpath", ""),
            )
            value = self.get_field_value(field_name, data)
            data_final[field_name] = value
        return fields_map, data_final

    async def fill_form_field(
            self,
            field_name: str,
            data: dict,
            map_label: dict[str, dict[str, Any]] | None = None,
            suffix: Optional[str] = ":",
    ):

        field_metadata = self.get_field_metadata(field_name, map_label)
        field_type = field_metadata.get("input_type", InputType.TEXT)
        field_label = field_metadata.get("label")
        label = f"{field_label}{suffix or ''}"

        value = self.get_field_value(field_name, data)

        xpath = await XPE.create(self.context,
                                 xpath=field_metadata.get("xpath"))
        await (await xpath.find_form_input(label, field_type)).handle_fill(
            str(value), field_type
        )

    async def fill_form_fields(
        self,
        data: dict,
        map_label: dict[str, dict[str, Any]] | None = None,
        suffix: Optional[str] = ":",
    ):
        breakpoint
        # Monta o dicionário de campos e os dados finais para preenchimento
        fields_map, final_data = self._mount_fields_map_and_data(
            data, map_label, suffix,
        )

        logger.debug(
            f"Preenchendo campos do formulário com dados: {final_data} "
            f"e mapeamento: {fields_map}"
        )

        for field_name, value in final_data.items():
            if field_name not in fields_map:
                logger.warning(
                    f"Campo '{field_name}' não está mapeado ou não é "
                    f"editável. Ignorado."
                )
                continue

            # Verificação do tipo esperado
            field_metadata = fields_map[field_name]
            if not (
                isinstance(field_metadata, dict)
                and len(field_metadata) == 4
                and all(isinstance(x, str) for x in field_metadata)
            ):
                raise TypeError(
                    f"O valor de campos_map['{field_name}'] deve ser uma "
                    f"dicionário montado a partir de 'SchemaMapExtractor.make_field_dict', "
                    f", mas foi recebido: {field_metadata!r}"
                )

            input_type = field_metadata.get("input_type", InputType.TEXT)
            xpath = await XPE.create(self.context,
                                     xpath=field_metadata.get("xpath"))
            await (await xpath.find_form_input(field_metadata.get("label"),
                                               input_type
                                               )).handle_fill(
                str(value), input_type
            )

    async def load_select_options(self, field_name: str):
        """
        Atualiza o mapeamento de opções de um campo <select> a partir da
        interface da página.

        Este método localiza o campo <select> relacionado ao nome do campo
        informado (`field_name`), extrai todas as opções disponíveis e
        atualiza o dicionário de mapeamento (`FIELDS_MAP`) com as opções
        atuais encontradas na página.

        Parâmetros
        ----------
        field_name : str
            Nome do campo cujo <select> terá as opções extraídas e mapeadas.

        Notas
        -----
        O método é útil para garantir que o mapeamento de valores do campo
        esteja sincronizado com a interface da aplicação, permitindo o
        preenchimento dinâmico dos campos de formulário conforme as opções
        realmente disponíveis na página no momento da execução.
        """
        field_metadata = self.get_field_metadata(field_name)
        xpath = await XPE.create(self.context,
                                 xpath=field_metadata.get("xpath"))
        await xpath.find_form_input(field_metadata.get("label"),
                                    field_metadata.get("input_type",
                                                       InputType.SELECT))
        await self.update_field_map_from_select(field_name, xpath)

    async def select_value(
        self, field_name: str, data: dict
    ) -> tuple[str, str] | list[tuple[str, str]]:
        """
        Preenche um campo de formulário identificado por `field_name` usando os dados fornecidos e retorna o texto visível e o valor selecionado (ou lista de tuplas para seleção múltipla). Usa o mapeamento FIELDS_MAP se existir. Lança exceção se o valor não for encontrado.
        """
        field_metadata = self.get_field_metadata(field_name)
        field_label = field_metadata.get("label")
        field_type = field_metadata.get("input_type", InputType.SELECT)

        xpath = await XPE.create(self.context,
                                 xpath=field_metadata.get("xpath"))

        type_exam_elem = await xpath.find_form_input(field_label, field_type)
        xpath_obj = await type_exam_elem.handle_fill(
            self.get_field_value(field_name, data), field_type, reset=False
        )
        value = await xpath_obj.get_value(field_type)

        # Para campos que retornam tupla (texto, valor)
        if isinstance(value, tuple):
            _, _value = value
            # Checa se existe o valor no FIELDS_MAP (se aplicável)
            if (
                field_name in self.FIELDS_MAP
                and _value not in self.FIELDS_MAP[field_name].values()
            ):
                raise FieldValueNotFoundError(self.context, field_name, _value)

        # Remove o campo do dicionário de dados após preenchimento
        data.pop(field_name, None)
        return value

    async def take_screenshot(
        self,
        filename: Optional[str] = None,
        full_page: bool = True,
        subdir: Optional[str] = None,
    ) -> Path:
        """Tira um screenshot da página atual e salva em arquivo."""
        page = await self.context.page  # page Playwright ativo no contexto
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        if subdir:
            Path(subdir).mkdir(parents=True, exist_ok=True)
            filepath = Path(subdir) / filename
        else:
            filepath = Path(filename)

        await page.screenshot(path=str(filepath), full_page=full_page)
        logger.info(f"Screenshot salvo em: {filepath.resolve()}")
        return filepath.resolve()
