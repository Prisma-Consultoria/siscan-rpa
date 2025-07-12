import os
import json
from pathlib import Path

import pytest
from faker import Faker
from validate_docbr import CNS
import brazilcep.client as bc
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Determine whether Playwright should run in headless mode. This can be
# controlled via the ``HEADLESS`` environment variable. If the variable is not
# defined, the default is ``True``.
HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"


@pytest.fixture(scope="session")
def headless() -> bool:
    """Return whether tests should run Playwright in headless mode."""
    return HEADLESS

ROOT = Path(__file__).resolve().parents[1]

priv = ROOT / "rsa_private_key.pem"
pub = ROOT / "rsa_public_key.pem"
if not priv.exists() or not pub.exists():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    priv.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    pub.write_bytes(
        key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )

from src.main import app  # noqa: E402


@pytest.fixture
def test_db(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("data") / "test.db"
    os.environ["DATABASE_URL"] = str(db_path)
    import src.env as env

    env.init_engine(str(db_path))
    from src import models  # noqa: F401

    env.Base.metadata.create_all(bind=env.engine)
    return db_path


@pytest.fixture
def client(test_db):
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def fake_json_file(tmp_path_factory):
    fake = Faker("pt_BR")
    cns = CNS()

    base_year = fake.random_int(min=2000, max=2025)

    cirurgias = [
        "biopsia_cirurgica_incisional",
        "biopsia_cirurgica_excisional",
        "segmentectomia",
        "centralectomia",
        "dutectomia",
        "mastectomia",
        "mastectomia_poupadora_pele",
        "mastectomia_poupadora_pele_complexo_papilar",
        "linfadenectomia_axilar",
        "biopsia_linfonodo_sentinela",
        "reconstrucao_mamaria",
        "mastoplastia_redutora",
        "inclusao_implantes",
    ]

    data = {
        "cartao_sus": cns.generate(),
        "nome": fake.name().upper(),
        "apelido": fake.first_name().upper(),
        "data_de_nascimento": fake.date_of_birth(
            minimum_age=30, maximum_age=80
        ).strftime("%d/%m/%Y"),
        "nacionalidade": "BRASILEIRO",
        "sexo": fake.random_element(elements=("F", "M")),
        "nome_da_mae": fake.name_female().upper(),
        "raca_cor": "BRANCA",
        "escolaridade": "4",
        "uf": fake.estado_sigla(),
        "municipio": fake.city().upper(),
        "tipo_logradouro": "RUA",
        "nome_logradouro": fake.street_name().upper(),
        "numero": str(fake.random_int(min=1, max=9999)),
        "bairro": fake.bairro().upper(),
        "cep": bc._format_cep(fake.postcode()),
        "ponto_de_referencia": "PONTO DE REFERÊNCIA",
        "unidade_requisitante": fake.numerify("#######"),
        "prestador": fake.company().upper(),
        "num_prontuario": fake.numerify("#########"),
        "tem_nodulo_ou_caroco_na_mama": ["01", "02"],
        "apresenta_risco_elevado_para_cancer_mama": "01",
        "fez_mamografia_alguma_vez": "01",
        "ano_que_fez_a_ultima_mamografia": str(base_year),
        "antes_desta_consulta_teve_as_mamas_examinadas_por_um_profissional": "03",
        "fez_radioterapia_na_mama_ou_no_plastrao": "01",
        "radioterapia_localizacao": "03",
        "ano_da_radioterapia_direita": str(base_year),
        "ano_da_radioterapia_esquerda": str(base_year),
        "fez_cirurgia_de_mama": "01",
        **{f"ano_{c}_direita": str(base_year + i) for i, c in enumerate(cirurgias)},
        **{
            f"ano_{c}_esquerda": str(base_year + i + 1) for i, c in enumerate(cirurgias)
        },
        "tipo_mamografia_de_rastreamento": "01",
        "data_da_solicitacao": fake.date_between(
            start_date="-30d", end_date="today"
        ).strftime("%d/%m/%Y"),
    }

    output_path = Path("./fake_data.json")
    # Always rewrite the fake data file to avoid stale content between test runs
    with open(output_path, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)

    return output_path
