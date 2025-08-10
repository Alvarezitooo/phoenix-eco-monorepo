import asyncio
import pytest

from phoenix_aube.services.data_providers import (
    DataAggregationService,
)


@pytest.mark.asyncio
async def test_enriched_job_data_smoke():
    async with DataAggregationService() as svc:
        res = await svc.get_enriched_job_data("Data Analyst")
        assert res["métier"] == "Data Analyst"
        assert "compétences_france_travail" in res


@pytest.mark.asyncio
async def test_market_analysis_smoke():
    async with DataAggregationService() as svc:
        res = await svc.get_comprehensive_market_analysis("Tech/IT")
        assert res["secteur"] == "Tech/IT"
        assert "tendances_compétences" in res

