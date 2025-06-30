# RPA SISCAN

Este projeto implementa uma automação (RPA) para interação com o sistema SIScan utilizando Playwright e FastAPI.

## Estrutura do projeto

- **run.py** – ponto de entrada que carrega variáveis de ambiente e executa o servidor FastAPI via Uvicorn.
- **src/main.py** – inicializa a aplicação FastAPI e registra as rotas.
- **src/routes/** – módulos de rotas da API:
  - `user.py` com `/user` (criação) e `/user/me` para obter o usuário autenticado.
    O endpoint `/user` exige o cabeçalho `Api-Key` válido e `/user/me` exige autenticação JWT.
  - `preencher_formulario_siscan.py` com `/preencher-formulario-siscan/solicitacao-mamografia` e `/preencher-formulario-siscan/laudo-mamografia`.
    Esses endpoints podem ser acessados com JWT ou com `Api-Key` registrada no banco de dados (e não expirada).
  Utiliza Playwright para abrir o navegador e ainda possui *TODOs* de implementação.
- **src/siscan/** – código principal de automação:
  - `context.py` controla o navegador e coleta mensagens informativas.
  - `siscan_webpage.py` define lógica comum de login e navegação.
  - `requisicao_exame.py` abstrai o preenchimento do formulário de exame.
  - `requisicao_exame_mamografia.py` especializa o fluxo para mamografia.
  - `webtools/` e `utils/` contêm classes de apoio (XPathConstructor, validação de esquemas, etc.).
  - `schema/` guarda arquivos JSON Schema para validação dos dados.
- **tests/** – casos de teste em pytest para os endpoints da API.

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
