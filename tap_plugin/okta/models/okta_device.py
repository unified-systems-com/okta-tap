"""Okta Device — A device registered in an Okta org through Okta Verify: its platform, status and whether it is managed."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class OktaDevice(BaseModel):
    """A device registered in an Okta org through Okta Verify: its platform, status and whether it is managed.

    A device Okta knows through Okta Verify registration. Devices are only ever observed, never
    designed, so the key is Okta's id.

    Spec: specs/spec-okta-v0.md (req-okta-corpus).
    """

    ENTITY_TYPE: ClassVar[str] = "okta__okta_device"
    ENTITY_NAME: ClassVar[str] = "Okta Device"
    ENTITY_DESCRIPTION: ClassVar[str] = "A device registered in an Okta org through Okta Verify: its platform, status and whether it is managed."
    ENTITY_ICON: ClassVar[str] = "okta-device"
    # No default dimension: the dcom value belongs to the observation (a seeded design node is
    # `design`, a collected one `configuration`), so whatever writes the node stamps it.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {}
    # Only a collector creates devices, and it always has the id.
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ('org_name', 'okta_id')
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#F1F5F9", "border": "#475569", "label": "#1E293B"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"type": "string", "minLength": 1},
        "okta_id": {"type": "string", "minLength": 1},
        "display_name": {"type": "string"},
        "platform": {"type": "string", "enum": ["", "ANDROID", "IOS", "MACOS", "WINDOWS"]},
        "os_version": {"type": "string"},
        "status": {"type": "string", "enum": ["", "ACTIVE", "DEACTIVATED", "SUSPENDED", "UNSUSPENDED"]},
        "managed": {"type": ["boolean", "null"]},
        "secure_hardware_present": {"type": ["boolean", "null"]},
        "tags": {"type": "object"},
    }
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "okta_id": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "display_name": {"validation": "jsonschema", "schema": {"type": "string"}},
        "platform": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "ANDROID", "IOS", "MACOS", "WINDOWS"]}},
        "os_version": {"validation": "jsonschema", "schema": {"type": "string"}},
        "status": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "ACTIVE", "DEACTIVATED", "SUSPENDED", "UNSUSPENDED"]}},
        "managed": {"validation": "jsonschema", "schema": {"type": ["boolean", "null"]}},
        "secure_hardware_present": {"validation": "jsonschema", "schema": {"type": ["boolean", "null"]}},
        "tags": {"validation": "jsonschema", "schema": {"type": "object"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["org_name", "okta_id"]

    #: The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping
    #: column, not a copy of the org: the org's own facts live on the org, and the
    #: BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold
    #: an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a
    #: column).
    org_name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's device id. Required: a device is only ever observed.
    okta_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: profile.displayName.
    display_name = models.CharField(max_length=255, blank=True, default="")
    #: profile.platform.
    platform = models.CharField(max_length=255, blank=True, default="")
    #: profile.osVersion.
    os_version = models.CharField(max_length=255, blank=True, default="")
    #: Okta's device status.
    status = models.CharField(max_length=255, blank=True, default="")
    #: Whether a device-management integration reports the device managed. Null means not observed.
    managed = models.BooleanField(null=True, blank=True)
    #: profile.secureHardwarePresent (TPM / Secure Enclave). Null means not observed.
    secure_hardware_present = models.BooleanField(null=True, blank=True)
    #: TAP's tag map.
    tags = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "okta__okta_device"

    def get_name(self) -> str:
        return self.display_name or self.okta_id or ""

    def __str__(self) -> str:
        return self.get_name()
