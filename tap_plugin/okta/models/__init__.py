"""TAP Okta models."""

from tap_plugin.okta.models.okta_admin_role import OktaAdminRole
from tap_plugin.okta.models.okta_api_token import OktaApiToken
from tap_plugin.okta.models.okta_application import OktaApplication
from tap_plugin.okta.models.okta_authenticator import OktaAuthenticator
from tap_plugin.okta.models.okta_authorization_server import OktaAuthorizationServer
from tap_plugin.okta.models.okta_device import OktaDevice
from tap_plugin.okta.models.okta_group import OktaGroup
from tap_plugin.okta.models.okta_group_rule import OktaGroupRule
from tap_plugin.okta.models.okta_identity_provider import OktaIdentityProvider
from tap_plugin.okta.models.okta_log_stream import OktaLogStream
from tap_plugin.okta.models.okta_network_zone import OktaNetworkZone
from tap_plugin.okta.models.okta_org import OktaOrg
from tap_plugin.okta.models.okta_policy import OktaPolicy
from tap_plugin.okta.models.okta_policy_rule import OktaPolicyRule
from tap_plugin.okta.models.okta_resource_set import OktaResourceSet
from tap_plugin.okta.models.okta_role_assignment import OktaRoleAssignment
from tap_plugin.okta.models.okta_trusted_origin import OktaTrustedOrigin
from tap_plugin.okta.models.okta_user import OktaUser

__all__ = [
    "OktaAdminRole",
    "OktaApiToken",
    "OktaApplication",
    "OktaAuthenticator",
    "OktaAuthorizationServer",
    "OktaDevice",
    "OktaGroup",
    "OktaGroupRule",
    "OktaIdentityProvider",
    "OktaLogStream",
    "OktaNetworkZone",
    "OktaOrg",
    "OktaPolicy",
    "OktaPolicyRule",
    "OktaResourceSet",
    "OktaRoleAssignment",
    "OktaTrustedOrigin",
    "OktaUser",
]
