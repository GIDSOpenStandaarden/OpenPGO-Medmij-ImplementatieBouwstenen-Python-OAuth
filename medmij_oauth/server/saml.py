import base64
import datetime
import urllib.parse
import zlib
import xml.etree.ElementTree as ET
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

def base64_url_encode(string_val):
    return urllib.parse.quote(
        base64.b64encode(string_val),
        safe=""
    )

def base64_url_decode(string_val):
    val = urllib.parse.unquote(string_val)
    return base64.b64decode(val)

def decode_url_param(b64string):
    decoded_data = base64_url_decode(b64string)

    try:
        return zlib.decompress(decoded_data)
    except Exception:
        # remove header
        return zlib.decompress(decoded_data, -15)

def encode_url_param_without_header(string_val):
    zlibbed_str = zlib.compress(string_val)
    return  base64_url_encode(zlibbed_str[2:-4])

def encode_url_param_with_header(string_val):
    zlibbed_str = zlib.compress(string_val)
    return  base64_url_encode(zlibbed_str)

def encode_url_param(string_val):
    return encode_url_param_without_header(string_val)

def sign(message):
    with open(os.getcwd() + "/trust/private.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    signature = private_key.sign(
        message.encode(),
        padding.PKCS1v15(),
        hashes.SHA1()
    )

    return signature

def parse_artifact(saml_art):
    _bytes = bytearray(base64_url_decode(saml_art))

    type_code = int(_bytes[0:2].hex(), 16)
    endpoint_index = int(_bytes[2:4].hex(), 16)
    remaning_artifact = _bytes[4:]
    source_id = remaning_artifact[0:20].hex()
    message_handle = remaning_artifact[20:]

    return (type_code, endpoint_index, source_id, message_handle)

class ContextClassRefs():
    BASIS = "urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport"
    MIDDEN = "urn:oasis:names:tc:SAML:2.0:ac:classes:MobileTwoFactorContract"
    SUBSTANTIEEL = "urn:oasis:names:tc:SAML:2.0:ac:classes:Smartcard"
    HOOG = "urn:oasis:names:tc:SAML:2.0:ac:classes:SmartcardPKI"

class SAMLRequestParams():
    def __init__(
            self,
            issuer="",
            issue_instant=datetime.datetime.now(),
            assertion_consumer_service_index=0,
            context_class_ref=ContextClassRefs.BASIS,
            force_authn=False,
            assertion_consumer_service_url=None,
            provider_name=None,
        ):
        self.issuer = issuer
        self.issue_instant = issue_instant
        self.assertion_consumer_service_index = assertion_consumer_service_index
        self.context_class_ref = context_class_ref
        self.force_authn = force_authn
        self.assertion_consumer_service_url = assertion_consumer_service_url
        self.provider_name = provider_name

    def to_xml_string(self):
        authn_request_element_attributes = {
            "xmlns:samlp": "urn:oasis:names:tc:SAML:2.0:protocol",
            "xmlns:saml": "urn:oasis:names:tc:SAML:2.0:assertion",
            "Version": "2.0",
            "IssueInstant": str(self.issue_instant)
        }

        if self.assertion_consumer_service_url:
            authn_request_element_attributes["AssertionConsumerServiceURL"] \
                = self.assertion_consumer_service_url
        else:
            authn_request_element_attributes["AssertionConsumerServiceIndex"] \
                = str(self.assertion_consumer_service_index)

        if self.provider_name:
            authn_request_element_attributes["ProviderName"] = self.provider_name

        authn_request_element = ET.Element("AuthnRequest", attrib=authn_request_element_attributes)

        issuer_element = ET.SubElement(authn_request_element, "saml:Issuer")
        issuer_element.text = self.issuer

        requested_auth_context_element = ET.SubElement(
            authn_request_element,
            "samlp:RequestedAuthnContext",
            attrib={"Comparison": "minimum"}
        )

        context_class_ref_element = ET.SubElement(
            requested_auth_context_element,
            "saml:AuthnContextClassRef"
        )

        context_class_ref_element.text = self.context_class_ref

        return ET.tostring(authn_request_element)

def build_request_query_params(params, relay_state):
    query_dict = {
        "SAMLRequest": encode_url_param(params.to_xml_string()),
        "RelayState": relay_state,
        "SigAlg": "http://www.w3.org/2000/09/xmldsig#rsa-sha1"
    }

    query_dict["Signature"] = base64_url_encode(sign(urllib.parse.urlencode(query_dict)))

    return urllib.parse.urlencode(query_dict)
