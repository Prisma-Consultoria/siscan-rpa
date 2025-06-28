# RPA SISCAN

Este projeto implementa uma automação (RPA) para interação com o sistema SIScan utilizando Playwright e FastAPI.

## Estrutura do projeto

- **run.py** – ponto de entrada que carrega variáveis de ambiente e executa o servidor FastAPI via Uvicorn.
- **src/main.py** – inicializa a aplicação FastAPI e registra as rotas.
- **src/routes/** – módulos de rotas da API:
  - `user.py` com `/user` (criação) e `/user/me` para obter o usuário autenticado.
  - `preencher_formulario_siscan.py` com `/preencher-formulario-siscan/solicitacao-mamografia` e `/preencher-formulario-siscan/laudo-mamografia`.
  Essas rotas aceitam autenticação via `Api-Key` (informando o UUID do usuário) ou JWT Bearer.
  Utiliza Playwright para abrir o navegador e ainda possui *TODOs* de implementação.
- **src/siscan/** – código principal de automação:
  - `context.py` controla o navegador e coleta mensagens informativas.
  - `siscan_webpage.py` define lógica comum de login e navegação.
  - `requisicao_exame.py` abstrai o preenchimento do formulário de exame.
  - `requisicao_exame_mamografia.py` especializa o fluxo para mamografia.
  - `webtools/` e `utils/` contêm classes de apoio (XPathConstructor, validação de esquemas, etc.).
  - `schemas/` guarda arquivos JSON Schema para validação dos dados.
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