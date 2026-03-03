import pytest
from pydantic import ValidationError

from app.schemas import EmpreendimentoCreate, MUNICIPIOS_SC


def _valid_data(**overrides) -> dict:
    base = {
        "nome_empreendimento": "Tech Solutions SC",
        "nome_empreendedor": "João Silva",
        "municipio": "Florianópolis",
        "segmento": "Tecnologia",
        "email": "joao@example.com",
        "status": "ativo",
    }
    base.update(overrides)
    return base


class TestEmpreendimentoCreate:
    def test_valid_creation(self):
        emp = EmpreendimentoCreate(**_valid_data())
        assert emp.nome_empreendimento == "Tech Solutions SC"
        assert emp.municipio == "Florianópolis"
        assert emp.segmento == "Tecnologia"

    def test_valid_without_email(self):
        emp = EmpreendimentoCreate(**_valid_data(email=None))
        assert emp.email is None

    def test_default_status_ativo(self):
        data = _valid_data()
        del data["status"]
        emp = EmpreendimentoCreate(**data)
        assert emp.status == "ativo"

    def test_invalid_municipio(self):
        with pytest.raises(ValidationError, match="município válido"):
            EmpreendimentoCreate(**_valid_data(municipio="Cidade Inexistente"))

    def test_invalid_segmento(self):
        with pytest.raises(ValidationError):
            EmpreendimentoCreate(**_valid_data(segmento="Mineração"))

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            EmpreendimentoCreate(**_valid_data(email="email-invalido"))

    def test_empty_nome_empreendimento(self):
        with pytest.raises(ValidationError, match="1 e 255"):
            EmpreendimentoCreate(**_valid_data(nome_empreendimento="   "))

    def test_empty_nome_empreendedor(self):
        with pytest.raises(ValidationError, match="1 e 255"):
            EmpreendimentoCreate(**_valid_data(nome_empreendedor=""))

    def test_all_segmentos_valid(self):
        for seg in ["Tecnologia", "Comércio", "Indústria", "Serviços", "Agronegócio"]:
            emp = EmpreendimentoCreate(**_valid_data(segmento=seg))
            assert emp.segmento == seg

    def test_municipios_list_has_295(self):
        assert len(MUNICIPIOS_SC) == 295

    def test_status_inativo(self):
        emp = EmpreendimentoCreate(**_valid_data(status="inativo"))
        assert emp.status == "inativo"

    def test_invalid_status(self):
        with pytest.raises(ValidationError):
            EmpreendimentoCreate(**_valid_data(status="pendente"))
