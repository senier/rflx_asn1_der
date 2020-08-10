from rflx.pyrflx import PyRFLX

SPECS = PyRFLX(["asn1_der.rflx"], True)
ASN1 = SPECS["ASN1_DER"]


def test_parse_null() -> None:
    message = ASN1["Message"]
    message.parse(bytes([5, 0]))


def test_parse_integer() -> None:
    message = ASN1["Message"]
    message.parse(bytes([2, 1, 47]))
    result = message.get("Negative")
    assert result == "False"
    assert message.get("Integer") == 47


def test_parse_bit_string() -> None:
    message = ASN1["Message"]
    message.parse(bytes([0x03, 0x04, 0x06, 0x6E, 0x5D, 0xC0]))
    assert message.get("Unused") == 6
    assert [d.value for d in message.get("Data")] == [0x6E, 0x5D]
    assert message.get("Last") == 0xC0
