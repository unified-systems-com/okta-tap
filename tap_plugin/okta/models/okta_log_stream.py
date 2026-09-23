"""Okta Log Stream — A log stream in an Okta org: the System Log delivered continuously to AWS EventBridge or Splunk Cloud."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class OktaLogStream(BaseModel):
    """A log stream in an Okta org: the System Log delivered continuously to AWS EventBridge or Splunk Cloud.

    Where the System Log goes. The destination node, when one exists, is reached by the open-ended
    WRITES_LOGS__okta edge.

    Spec: specs/spec-okta-v0.md (req-okta-corpus).
    """

    ENTITY_TYPE: ClassVar[str] = "okta__okta_log_stream"
    ENTITY_NAME: ClassVar[str] = "Okta Log Stream"
    ENTITY_DESCRIPTION: ClassVar[str] = "A log stream in an Okta org: the System Log delivered continuously to AWS EventBridge or Splunk Cloud."
    ENTITY_ICON: ClassVar[str] = "okta-log-stream"
    # No default dimension: the dcom value belongs to the observation (a seeded design node is
    # `design`, a collected one `configuration`), so whatever writes the node stamps it.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {}
    # Names are unique within an org; revisited to (org_name, okta_id).
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ('org_name', 'name')
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#F1F5F9", "border": "#475569", "label": "#1E293B"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"type": "string", "minLength": 1},
        "name": {"type": "string", "minLength": 1},
        "okta_id": {"type": "string"},
        "stream_type": {"type": "string", "enum": ["", "aws_eventbridge", "splunk_cloud_logstreaming"]},
        "status": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE"]},
        "destination": {"type": "string"},
        "configuration": {"type": "object"},
        "tags": {"type": "object"},
    }
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "okta_id": {"validation": "jsonschema", "schema": {"type": "string"}},
        "stream_type": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "aws_eventbridge", "splunk_cloud_logstreaming"]}},
        "status": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE"]}},
        "destination": {"validation": "jsonschema", "schema": {"type": "string"}},
        "configuration": {"validation": "jsonschema", "schema": {"type": "object"}},
        "tags": {"validation": "jsonschema", "schema": {"type": "object"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["org_name", "name"]

    #: The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping
    #: column, not a copy of the org: the org's own facts live on the org, and the
    #: BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold
    #: an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a
    #: column).
    org_name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: The log stream's name.
    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
    okta_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's log stream type.
    stream_type = models.CharField(max_length=255, blank=True, default="")
    #: Okta's status.
    status = models.CharField(max_length=255, blank=True, default="")
    #: Where the stream lands, in the destination's own words: an EventBridge event source (account,
    #: region, source name) or a Splunk host.
    destination = models.CharField(max_length=255, blank=True, default="")
    #: The remainder of the object as Okta returns it; nothing identity-bearing lives here.
    configuration = models.JSONField(default=dict, blank=True)
    #: TAP's tag map.
    tags = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "okta__okta_log_stream"

    def get_name(self) -> str:
        return self.name or ""

    def __str__(self) -> str:
        return self.get_name()
