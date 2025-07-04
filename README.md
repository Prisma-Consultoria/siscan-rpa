# RPA SISCAN

Este projeto implementa uma automação (RPA) para interação com o sistema SIScan utilizando Playwright e FastAPI.

## Estrutura do projeto

- **run.py** – ponto de entrada que carrega variáveis de ambiente e executa o servidor FastAPI via Uvicorn.
- **src/main.py** – inicializa a aplicação FastAPI e registra as rotas.
- **src/routes/** – módulos de rotas da API:
  - `user.py` com `/user` (criação) e `/user/me` para obter o usuário autenticado. O primeiro requer o cabeçalho `Api-Key` válido e o segundo exige JWT.
  - `preencher_formulario_siscan.py` implementa os fluxos de formulário de mamografia nos endpoints
    `/requisicao-mamografia-rastreamento`, `/requisicao-mamografia-diagnostica` e `/laudo-mamografia`.
    Todos podem ser acessados com JWT ou com uma `Api-Key` registrada e válida.
  - `security.py` para geração de token JWT em `/security/token`.
  Utiliza Playwright para abrir o navegador (ainda existem *TODOs* de implementação).
- **src/siscan/** – código principal de automação:
  - `context.py` controla o navegador e coleta mensagens informativas.
  - `classes/webpage.py` define lógica comum de login, navegação e acesso a menus.
  - `requisicao_exame.py` abstrai o preenchimento do formulário de exame.
  - `requisicao_exame_mamografia.py` especializa o fluxo para mamografia.
  - `classes/` contém variações específicas do fluxo de requisição (rastreio, diagnóstica etc.).
  - `utils/` possui classes de apoio como `XPathConstructor`, validação de esquemas e utilitários.
-  - `schema/` guarda arquivos JSON Schema para validação dos dados.
- **tests/** – casos de teste em pytest para os endpoints da API.

## Arquitetura do projeto

Esta aplicação é composta por uma API FastAPI que aciona rotinas de
automação com o Playwright. O banco de dados utiliza SQLAlchemy (SQLite
por padrão) e as entradas são validadas com Pydantic.

### Principais classes e abstrações

- **`SiscanBrowserContext`** (`src/siscan/context.py`) – inicializa o
  navegador e mantém a página ativa, além de coletar mensagens da popup
  de informações.
- **`WebPage`** (`src/utils/webpage.py`) – base genérica para páginas com
  suporte a captura de screenshot, carregamento de opções de campos e
  mapeamento de valores.
- **`SiscanWebPage`** (`src/siscan/classes/webpage.py`) – estende
  `WebPage` com a lógica de login e navegação. O método `acessar_menu`
  utiliza tentativas sucessivas para abrir menus do SIScan até que a
  ação tenha sucesso ou o tempo limite seja alcançado.
- **`RequisicaoExame`** e subclasses – definem o fluxo de preenchimento
  dos formulários de exame. Existem especializações para mamografia de
  rastreamento e diagnóstica, cada uma carregando seu JSON Schema para
  criar os mapas de campos automaticamente.
- **`XPathConstructor`** (`src/utils/xpath_constructor.py`) – utilitário
  para construir XPaths e interagir com elementos. Possui métodos de
  retry para seleção de menus, preenchimento de campos e leitura de
  valores.
- **`SchemaMapExtractor`** e **`Validator`** – auxiliam na extração de
  metadados de schemas e validação dos dados enviados para os endpoints.

Essas abstrações permitem reutilizar ações comuns, como abrir menus ou
preencher campos, facilitando a criação de novos fluxos de automação.

## Gerar chaves RSA

Necessário pra serviço de criptografia de senhas do banco de dados.

```bash
openssl genpkey -algorithm RSA -out rsa_private_key.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in rsa_private_key.pem -out rsa_public_key.pem
```

## Variáveis de ambiente


```bash
cp .env.example .env
```

## Executando

Para rodar localmente:

```bash
conda create -n siscan python=3.11
conda activate siscan
python run.py
```

Ou com Docker Compose:

```bash
docker compose up -d --build
```

### Criar ApiKey

Gere uma chave de acesso para clientes externos executando:

```bash
python cli.py create-apikey
```

## Rodando testes
Instale os navegadores do Playwright uma vez antes de rodar os testes:

```bash
playwright install
```

Para visualizar as mensagens de `print` e `logger.debug` utilize a flag `-s`:

```bash
pytest -s
DEBUG=pw:api pytest -s tests/test_playwright_flow.py
PWDEBUG=1 DEBUG=pw:api pytest -s tests/test_playwright_flow.py --headed --browser chromium

```

## Documentação

Acesse [http://localhost:5001/docs](http://localhost:5001/docs) para visualizar a documentação da API e testar seus endpoints


## Reference SDK

O código de automação organiza algumas estruturas de mapeamento utilizadas nos fluxos de preenchimento. A seguir estão as principais definições:

- **`FIELDS_MAP`** – dicionário que relaciona cada campo do formulário a um mapeamento de opções válidas. Ele converte valores fornecidos nos dados para os valores requeridos pelos elementos HTML (value de `<select>`, radio, etc.).
- **`MAP_DATA_LABEL`** – dicionário onde a chave é o nome do campo e o valor é uma tupla `(label, tipo, obrigatoriedade)` definindo o texto exibido, o tipo de input e o nível de obrigatoriedade.
- **`MAP_SCHEMA_FIELDS`** – lista com os nomes de campos extraídos do JSON Schema para compor os mapas anteriores. Cada classe define sua própria lista de campos relevantes.

O utilitário `SchemaMapExtractor.schema_to_maps()` lê um JSON Schema e retorna dois dicionários:

1. `map_data_label`: no formato de `MAP_DATA_LABEL` descrito acima;
2. `fields_map`: no formato de `FIELDS_MAP` para campos definidos como `enum` ou `array[enum]` no schema.

Esses mapas são utilizados pelas classes de página para validar e preencher automaticamente os formulários do SIScan.
