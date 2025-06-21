from pathlib import Path
from datetime import datetime
import logging
from abc import abstractmethod, ABC
from enum import Enum
from typing import Optional, Union

from src.siscan.exception import FieldValueNotFoundError
from src.siscan.webtools.xpath_constructor import XPathConstructor, InputType
from src.siscan.context import SiscanBrowserContext

logger = logging.getLogger(__name__)


class RequirementLevel(Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"

    # Ou, para uso de instância:
    def is_required(self) -> bool:
        """
        Verifica se a instância representa o nível 'required'.
        """
        return self is RequirementLevel.REQUIRED


class WebPage(ABC):
    """
    Classe abstrata para navegação de páginas desde a página de origem e autenticação
    """

    FIELDS_MAP: dict[str, dict[str, str]] = {}

    def __init__(self, url_base: str, user: str, password: str,
                 schema_path: Union[str, Path]):
        self._url_base = url_base
        self._user = user
        self._password = password
        self._schema_path = schema_path
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
            url_base=self._url_base,
            headless=False,  # Para depuração, use False
            timeout=15000
        )
        self.authenticate()


    @abstractmethod
    def authenticate(self):
        raise NotImplementedError("Subclasses devem implementar este método.")

    @abstractmethod
    def get_map_label(self) -> dict[str, tuple[str, str]]:
        """
        Método abstrato que deve ser implementado por subclasses para retornar
        o mapeamento de labels. Deve retornar um dicionário onde as chaves
        são os nomes dos campos e os valores são tuplas contendo o label e o
        tipo do campo.
        """
        raise NotImplementedError("Subclasses devem implementar este método.")

    @abstractmethod
    def validation(self, data: dict):
        raise NotImplementedError("Subclasses devem implementar este método.")

    @property
    def schema_path(self):
        return self._schema_path

    def get_field_metadata(
            self,
            field_name: str,
            map_label: Optional[dict[str, tuple]] = None
    ) -> tuple[str, InputType, RequirementLevel]:
        """
        Retorna o label, o tipo e o indicador de obrigatoriedade de um campo,
        baseado no mapeamento fornecido.

        Este método consolida a busca das principais informações do campo de
        formulário: o texto do label exibido ao usuário, o tipo do campo e se
        o preenchimento é obrigatório.

        Parâmetros
        ----------
        field_name : str
            Nome lógico do campo para o qual se deseja obter as informações.
        map_label : Optional[dict[str, tuple]], opcional
            Dicionário de mapeamento de campos. Caso não seja informado,
            utiliza o mapeamento padrão retornado por `get_map_label()`.

        Retorno
        -------
        tuple (label, tipo, required)
            - label: str - Texto do label conforme definido no mapeamento.
            - tipo: str - Tipo do campo (exemplo: 'text', 'select',
                'checkbox').
            - required: bool - True se o campo é obrigatório, False caso
                contrário.

        Exceções
        --------
        ValueError
            Disparada se o campo não estiver presente no mapeamento fornecido
            ou se não houver informação suficiente sobre obrigatoriedade.

        Exemplo
        -------
        ```
        label, tipo, required = self.get_field_metadata(
        "ano_que_fez_a_ultima_mamografia")
        print(label, tipo, required)
        # "QUANDO FEZ A ÚLTIMA MAMOGRAFIA?", InputType.TEXT, True
        ```
        """
        # Busca o valor no dicionário de mapeamento
        if map_label is None:
            value = self.get_map_label().get(field_name)
        else:
            value = map_label.get(field_name)

        if value is None:
            raise ValueError(f"Campo '{field_name}' não está mapeado.")

        if len(value) != 3:
            raise ValueError(
                f"O campo '{field_name}' não possui indicação de "
                f"obrigatoriedade no mapeamento."
            )
        return value

    def get_field_label(
            self, field_name: str,
            map_label: Optional[dict[str, tuple[str, str]]] = None) -> str:
        """
        Retorna o texto do label associado ao nome lógico do campo, com base no
        mapeamento informado.

        Este método busca a tupla (label, tipo) correspondente ao campo no
        dicionário de mapeamento (`map_label` se fornecido, caso contrário o
        mapeamento padrão retornado por `get_map_label()`). Em seguida,
        retorna a posição 0 da tupla, correspondente ao texto do label
        apresentado na tela.

        Parâmetros
        ----------
        campo : str
            Nome lógico do campo para o qual se deseja obter o label.
        map_label : Optional[dict[str, tuple[str, str]]], opcional
            Dicionário de mapeamento de campos. Caso não seja informado,
            utiliza o mapeamento padrão retornado por `get_map_label()`.

        Retorno
        -------
        str
            Texto do label conforme definido no mapeamento.

        Exceções
        --------
        ValueError
            Disparada se o campo não estiver presente no mapeamento fornecido.

        Exemplo
        -------
        ```
        label = self.get_label("unidade_requisitante")
        print(label)
        # 'Unidade Requisitante'
        ```
        """
        if map_label is None:
            value = self.get_map_label().get(field_name)
        else:
            value = map_label.get(field_name)

        if value is None:
            raise ValueError(f"Campo '{field_name}' não está mapeado.")
        return value[0]

    def get_field_type(
            self, field_name: str,
            map_label: Optional[dict[str, tuple[str, str]]] = None) -> str:
        """
        Retorna o tipo de campo associado ao nome lógico do campo, com base no
        mapeamento informado.

        Este método recupera a tupla (label, tipo) correspondente ao campo no
        dicionário de mapeamento (`map_label` se fornecido, caso contrário o
        mapeamento padrão do objeto). Em seguida, retorna a posição 1 da tupla,
        correspondente ao tipo do campo (por exemplo, 'text', 'select',
        'checkbox').

        Parâmetros
        ----------
        campo : str
            Nome lógico do campo para o qual se deseja obter o tipo.
        map_label : Optional[dict[str, tuple[str, str]]], opcional
            Dicionário de mapeamento de campos. Caso não seja informado,
            utiliza o mapeamento padrão retornado por `get_map_label()`.

        Retorno
        -------
        str
            Tipo do campo conforme definido no mapeamento (por exemplo, 'text',
            'select', 'date', 'checkbox').

        Exceções
        --------
        ValueError
            Disparada se o campo não estiver presente no mapeamento fornecido.

        Exemplo
        -------
        ```
        tipo = self.get_label_type("unidade_requisitante")
        print(tipo)
        # 'select'
        ```
        """
        if map_label is None:
            value = self.get_map_label().get(field_name)
        else:
            value = map_label.get(field_name)

        if value is None:
            raise ValueError(f"Campo '{field_name}' não está mapeado.")
        return value[1]

    def get_field_required(
            self, field_name: str,
            map_label: Optional[dict[str, tuple[str, str]]] = None) -> str:
        if map_label is None:
            value = self.get_map_label().get(field_name)
        else:
            value = map_label.get(field_name)

        if value is None:
            raise ValueError(f"Campo '{field_name}' não está mapeado.")
        return value[2]

    def get_field_value(
            self, field_name: str, data: dict) -> Optional[str | list]:
        """
        Obtém o valor correspondente ao campo informado, realizando a conversão
        conforme o mapeamento definido em `FIELDS_MAP`, caso aplicável.

        Este método busca o valor do campo no dicionário de dados `data`. Se o
        campo possuir um mapeamento definido em `FIELDS_MAP` e o valor não for
        nulo, realiza a conversão para o valor esperado pela interface (por
        exemplo, converter "Masculino" para "M", "Ensino Médio Completo" para
        "4" etc.). Caso não haja mapeamento ou o valor seja nulo, retorna o
        valor original obtido do dicionário.

        Parâmetros
        ----------
        campo : str
            Nome do campo cujo valor se deseja obter e converter.
        data : dict
            Dicionário contendo os dados de entrada do formulário.

        Retorno
        -------
        Optional[str | list]
            Valor convertido de acordo com o mapeamento definido, se aplicável.
            Caso contrário, retorna o valor original do campo ou None.
        """
        value = data.get(field_name, None)

        if field_name in self.FIELDS_MAP.keys() and value is not None:
            # Mapeia o valor do campo para o valor específico definido no
            # mapeamento
            if isinstance(value, list):
                logger.warning(
                    f"O valor do campo '{field_name}' é uma lista ({value}). "
                    f"O mapeamento FIELDS_MAP espera um valor escalar. "
                    f"Ignorando o mapeamento e retornado o valor real "
                    f"fornecido em 'data'.")
            else:
                value = self.FIELDS_MAP[field_name].get(value, None)
        return value

    def update_field_map_from_select(
            self,
            field_name: str,
            xpath: XPathConstructor,
            label_as_key: bool = True,
            timeout: int = 10
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
        options = xpath.get_select_options(timeout=timeout)
        if label_as_key:
            mapping = {label: value for value, label in options.items()}
        else:
            mapping = {value: label for value, label in options.items()}
        self.FIELDS_MAP[field_name] = mapping
        xpath.reset()

    def mount_fields_map_and_data(
            self, data: dict,
            map_label: dict[str, tuple[str, str]],
            suffix: Optional[str] = ":"
    ) -> tuple[dict[str, tuple[str, str]], dict[str, str]]:
        """
        Gera o dicionário campos_map e o dicionário data_final para uso em
        preenchimento genérico de formulários.

        Parâmetros
        ----------
        data : dict
            Dicionário de dados originais (nomes de campos como chave).
        map_label : dict[str, tuple[str, str]]
            Dicionário com nomes de campos como chave e tuplas contendo
            (label, tipo de campo) como valor.
        suffix : str, opcional (default=":")

        Retorna
        -------
        tuple (campos_map, data_final)
            - campos_map: dict[str, tuple[str, str]]
            - data_final: dict[str, str]
        """
        if suffix is None:
            suffix = ""

        fields_map = {}
        data_final = {}
        for field_name in data.keys():
            if field_name not in map_label.keys():
                logger.warning(f"Campo '{field_name}' não está mapeado ou não "
                               f"é editável. Ignorado.")
                continue
            field_label, field_type, requirement_level = (
                self.get_field_metadata(field_name, map_label))
            value = self.get_field_value(field_name, data)
            fields_map[field_name] = (f"{field_label}{suffix}",
                                      field_type,
                                      requirement_level)
            data_final[field_name] = value
        return fields_map, data_final

    def load_select_options(self, field_name: str):
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
        xpath = XPathConstructor(self.context)
        field_label, field_type, _ = self.get_field_metadata(field_name)
        xpath.find_form_input(field_label, field_type)
        self.update_field_map_from_select(field_name, xpath)

    def select_value(
            self, field_name: str, data: dict
    ) -> tuple[str, str] | list[tuple[str, str]]:
        """
        Seleciona ou preenche um valor em um campo de formulário identificado
        pelo nome lógico do campo e retorna uma tupla contendo o texto visível
        e o valor efetivamente selecionado, ou uma lista de tuplas no caso de
        múltipla seleção.

        Este método localiza dinamicamente o elemento de formulário (input,
        select, radio, checkbox etc.) associado ao campo especificado por
        `field_name`, converte o valor informado conforme necessário (usando o
        mapeamento definido em `FIELDS_MAP`, se existir) e realiza o
        preenchimento/seleção no campo correspondente da página.

        O valor selecionado é extraído do dicionário `data` e convertido
        automaticamente para o valor esperado pela interface, caso exista
        mapeamento definido para esse campo. Após o preenchimento/seleção, o
        método retorna uma tupla (`texto`, `value`) correspondente ao que está
        selecionado no campo de formulário (exatamente como será enviado ao
        backend). Para campos do tipo múltipla escolha (checkbox múltiplo),
        retorna uma lista de tuplas.

        Parâmetros
        ----------
        field_name : str
            Nome lógico do campo do formulário a ser preenchido ou selecionado.
        data : dict
            Dicionário de dados contendo os valores de preenchimento para os
            campos do formulário.

        Retorno
        -------
        tuple[str, str] ou list[tuple[str, str]]
            Tupla contendo (texto visível, valor efetivamente selecionado) no
            campo, ou lista de tuplas em caso de seleção múltipla (ex:
            múltiplos checkboxes).
            O valor retornado corresponde ao valor submetido à aplicação
            (por exemplo, o atributo `value` do `<option>` selecionado em
             um `<select>`).

        Exceções
        --------
        SiscanFieldValueNotFoundError
            Lançada quando o valor selecionado não é encontrado no mapeamento
            `FIELDS_MAP`, indicando inconsistência ou valor inválido.

        Notas
        -----
        - Este método é apropriado para campos dos tipos `select`, `radio`,
          `checkbox` (único ou múltiplo) e também campos de texto, desde que a
          implementação do método `fill` do `XPathConstructor` suporte o tipo
          de campo.
        - O valor preenchido é extraído de `data[field_name]` e, se existir um
          mapeamento em `FIELDS_MAP`, será convertido automaticamente para o
          valor correspondente esperado pela interface.
        - É recomendável que o dicionário de dados (`data`) esteja sincronizado
          com o mapeamento de campos esperado pelo formulário.
        - O valor retornado corresponde ao valor efetivamente selecionado no
          campo, conforme será submetido à aplicação (por exemplo, o atributo
          `value` do `<option>` selecionado em um `<select>`).

        Exemplo
        -------
        ```
        data = {"sexo": "Masculino"}
        texto, value = self.select_value("sexo", data)
        print(texto, value)
        # 'Feminino', 'F'
        # O campo 'sexo' será preenchido com o valor mapeado ('F') no
        #  formulário, e o método retorna ('Feminino', 'F') como tupla
        #  correspondente.
        lista = self.select_value("caracteristicas", data)
        print(lista)
        [('Característica 1', '1'), ('Característica 2', '2')]
        # Para campos múltiplos, retorna uma lista de tuplas (texto, valor).
        ```
        """
        xpath = XPathConstructor(self.context)
        field_label, field_type, _ = self.get_field_metadata(field_name)

        type_exam_elem = xpath.find_form_input(field_label, field_type)
        xpath_obj = type_exam_elem.fill(self.get_field_value(field_name, data),
                                        field_type,
                                        reset=False)
        value = xpath_obj.get_value(field_type)
        # Para campos que retornam tupla (texto, valor)
        if isinstance(value, tuple):
            _, _value = value
            # Checa se existe o valor no FIELDS_MAP (se aplicável)
            if (field_name in self.FIELDS_MAP
                    and _value not in self.FIELDS_MAP[field_name].values()):
                raise FieldValueNotFoundError(self.context, field_name, _value)
        return value

    def take_screenshot(self, filename: Optional[str] = None, full_page: bool = True, subdir: Optional[str] = None) -> Path:
        """
        Realiza um screenshot (print da tela) da página atual e salva em arquivo.

        Parâmetros
        ----------
        filename : Optional[str], default=None
            Nome do arquivo de imagem a ser salvo (ex: 'tela.png').
            Se não informado, gera nome automático com timestamp.
        full_page : bool, default=True
            Se True, captura a página completa. Caso False, apenas o viewport visível.
        subdir : Optional[str], default=None
            Diretório para salvar o print. Se None, salva no diretório corrente.

        Retorno
        -------
        Path
            Caminho absoluto do arquivo de imagem salvo.

        Exemplo
        -------
        ```python
        caminho = self.take_screenshot()
        print(f"Print salvo em: {caminho}")
        ```
        """
        page = self.context.page  # page Playwright ativo no contexto
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        if subdir:
            Path(subdir).mkdir(parents=True, exist_ok=True)
            filepath = Path(subdir) / filename
        else:
            filepath = Path(filename)
        page.screenshot(path=str(filepath), full_page=full_page)
        logger.info(f"Screenshot salvo em: {filepath.resolve()}")
        return filepath.resolve()