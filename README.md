# RPA SISCAN

## Gerar chaves RSA
```bash
openssl genpkey -algorithm RSA -out rsa_private_key.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in rsa_private_key.pem -out rsa_public_key.pem
```

## Variáveis de ambiente

```bash
PRODUCTION=false
TAKE_SCREENSHOT=true
DATABASE_URL=users.db
```

## Executar com Docker Compose

```bash
docker compose up -d --build
```

