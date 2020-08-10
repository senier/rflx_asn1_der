from rflx.pyrflx import PyRFLX

SPECS = PyRFLX(["asn1_der.rflx"], True)
ASN1 = SPECS["ASN1_DER"]


def test_parse_null() -> None:
    message = ASN1["Message"]
    message.parse(bytes([5, 0]))
