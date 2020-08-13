import pytest

from rflx.pyrflx import MessageValue, PyRFLX

SPECS = PyRFLX(["asn1_der.rflx"], True)
ASN1 = SPECS["ASN1_DER"]


def test_parse_null() -> None:
    message = ASN1["Message"]
    message.parse(bytes([5, 0]))


def test_parse_integer() -> None:
    message = ASN1["Message"]
    message.parse(bytes([2, 1, 47]))
    assert message.get("Integer_Flag") == "False"
    assert message.get("Integer_Value") == 47


def test_parse_bit_string() -> None:
    message = ASN1["Message"]
    message.parse(bytes([0x03, 0x04, 0x06, 0x6E, 0x5D, 0xC0]))
    assert message.get("Unused") == 6
    assert [d.value for d in message.get("Data")] == [0x6E, 0x5D, 0xC0]


@pytest.mark.skip(reason="ISSUE: Componolit/RecordFlux#")
def test_parse_bit_string_invalid_unused() -> None:
    message = ASN1["Message"]
    with pytest.raises(ValueError):
        message.parse(bytes([0x03, 0x04, 0x06, 0x6E, 0x5D, 0xC1]))


def test_parse_octet_string() -> None:
    message = ASN1["Message"]
    message.parse(bytes([0x04, 0x04, 0x03, 0x02, 0x06, 0xA0]))
    assert [d.value for d in message.get("Data")] == [0x03, 0x02, 0x06, 0xA0]


@pytest.mark.skip(reason="ISSUE: Componolit/RecordFlux#401")
def test_parse_integers() -> None:
    def value(message: MessageValue) -> int:
        m = message
        while True:
            yield m.get("Chunk_Value")
            if m.get("Chunk_Flag") == "False":
                break
            m = m.get("Next")

    m1 = ASN1["Integer_List"]
    m1.parse(bytes([0x82, 0x42]))
    assert list(value(m1)) == [0x02, 0x42]

    m1 = ASN1["Integer_List"]
    m1.parse(bytes([0x90, 0xA0, 0xB0, 0xC0, 0x50]))
    assert list(value(m1)) == [0x10, 0x20, 0x30, 0x40, 0x50]
