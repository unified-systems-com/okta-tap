"""Behaviour tests for okta__okta_org (req-okta-model)."""

from __future__ import annotations

import pytest
from tap_plugin.okta.models import OktaOrg

from tap_grid.caller_context import CallerContext
from tap_grid.services import WriteOperation, write_batch

TYPE = "okta__okta_org"


@pytest.mark.django_db
class TestOktaOrg:
    def test_create_with_name_only(self) -> None:
        """req-okta-model-1: a design-phase node needs only its name."""
        result = write_batch(
            [WriteOperation(verb="create_node", type_slug=TYPE, payload={"name": "staging"})],
            caller_context=CallerContext(),
        )
        assert result.results[0].success
        row = OktaOrg.all_objects.get(entity_id=result.results[0].entity_id)
        assert row.name == "staging"
        assert row.org_domain == ""

    def test_name_required(self) -> None:
        """req-okta-model-2: a write without a name is refused."""
        result = write_batch(
            [WriteOperation(verb="create_node", type_slug=TYPE, payload={"org_domain": "x"})],
            caller_context=CallerContext(),
        )
        assert not result.results[0].success


def test_keyed_by_name() -> None:
    """req-okta-model-3: the key rests only on a field the model carries."""
    assert OktaOrg.NATURAL_KEY == ("name",)
    names = {f.name for f in OktaOrg._meta.get_fields()}
    assert all(k in names for k in OktaOrg.NATURAL_KEY)
