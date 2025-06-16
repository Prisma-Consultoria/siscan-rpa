import logging
from abc import abstractmethod, ABC

from src.siscan.exception import FieldValueNotFoundError
from src.siscan.webtools.xpath_constructor import XPathConstructor
from typing import Optional

from src.siscan.context import SiscanBrowserContext

logger = logging.getLogger(__name__)


class WebPage(ABC):
    # Mapeamento de campos para valores específicos
    FIELDS_MAP: dict[str, dict[str, str]] = {}

    def __init__(self, url_base: str):
        self._url_base = url_base
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

    def get_label(
            self, campo: str,
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
            value = self.get_map_label().get(campo)
        else:
            value = map_label.get(campo)

        if value is None:
            raise ValueError(f"Campo '{campo}' não está mapeado.")
        return value[0]

    def get_label_type(
            self, campo: str,
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
            value = self.get_map_label().get(campo)
        else:
            value = map_label.get(campo)

        if value is None:
            raise ValueError(f"Campo '{campo}' não está mapeado.")
        return value[1]

    def get_value(self, campo: str, data: dict) -> Optional[str | list]:
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
        value = data.get(campo, None)

        if campo in self.FIELDS_MAP.keys() and value is not None:
            # Mapeia o valor do campo para o valor específico definido no
            # mapeamento
            value = self.FIELDS_MAP[campo].get(value, None)
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
        xpath.find_form_input("Unidade de Saúde", "select")
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
        xpath.find_form_input(self.get_label(field_name),
                              self.get_label_type(field_name))
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
        type_exam_elem = xpath.find_form_input(
            self.get_label(field_name),
            self.get_label_type(field_name)
        )
        xpath_obj = type_exam_elem.fill(self.get_value(field_name, data),
                                        self.get_label_type(field_name),
                                        reset=False)
        value = xpath_obj.get_value()
        # Para campos que retornam tupla (texto, valor)
        if isinstance(value, tuple):
            _, _value = value
            # Checa se existe o valor no FIELDS_MAP (se aplicável)
            if (field_name in self.FIELDS_MAP
                    and _value not in self.FIELDS_MAP[field_name].values()):
                raise FieldValueNotFoundError(self.context, field_name, _value)
        return value

