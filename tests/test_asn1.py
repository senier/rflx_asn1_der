from typing import Generator

import pytest

from rflx.pyrflx import MessageValue, PyRFLX

SPECS = PyRFLX(["asn1.rflx"], True)
ASN1 = SPECS["ASN1"]


def test_parse_null() -> None:
    message = ASN1["NUL"]
    message.parse(bytes([0]))


def test_parse_integer() -> None:
    message = ASN1["UNTAGGED_INTEGER"]
    message.parse(bytes([1, 47]))
    assert message.get("Integer_Flag") == "False"
    assert message.get("Integer_Value") == 47

    message = ASN1["INTEGER"]
    message.parse(bytes([2, 1, 47]))
    assert message.get("T_Integer_Flag") == "False"
    assert message.get("T_Integer_Value") == 47


def test_parse_bit_string() -> None:
    message = ASN1["BIT_STRING"]
    message.parse(bytes([0x04, 0x06, 0x6E, 0x5D, 0xC0]))
    assert message.get("Unused") == 6
    data = message.get("Value")
    assert isinstance(data, list)
    assert [d.value for d in data] == [0x6E, 0x5D, 0xC0]


@pytest.mark.skip(reason="ISSUE: Componolit/RecordFlux#")
def test_parse_bit_string_invalid_unused() -> None:
    message = ASN1["BIT_STRING"]
    with pytest.raises(ValueError):
        message.parse(bytes([0x04, 0x06, 0x6E, 0x5D, 0xC1]))


def test_parse_octet_string() -> None:
    message = ASN1["OCTET_STRING"]
    message.parse(bytes([0x04, 0x03, 0x02, 0x06, 0xA0]))
    data = message.get("Value")
    assert isinstance(data, list)
    assert [d.value for d in data] == [0x03, 0x02, 0x06, 0xA0]


@pytest.mark.skip(reason="ISSUE: Componolit/RecordFlux#401")
def test_parse_integers() -> None:
    def value(message: MessageValue) -> Generator[int, None, None]:
        m: MessageValue = message
        while True:
            result = m.get("Chunk_Value")
            assert isinstance(result, int)
            yield result
            if m.get("Chunk_Flag") == "False":
                break
            nxt = m.get("Next")
            assert isinstance(nxt, MessageValue)
            m = nxt

    m1 = ASN1["Integer_List"]
    m1.parse(bytes([0x82, 0x42]))
    assert list(value(m1)) == [0x02, 0x42]

    m1 = ASN1["Integer_List"]
    m1.parse(bytes([0x90, 0xA0, 0xB0, 0xC0, 0x50]))
    assert list(value(m1)) == [0x10, 0x20, 0x30, 0x40, 0x50]


def test_parse_utctime() -> None:
    message = ASN1["UTCTime"]
    date = chr(13) + "860923175628Z"
    message.parse(date.encode("ascii"))
    fields = [
        "U_Year_H",
        "U_Year_L",
        "U_Month_H",
        "U_Month_L",
        "U_Day_H",
        "U_Day_L",
        "U_Hour_H",
        "U_Hour_L",
        "U_Minute_H",
        "U_Minute_L",
        "U_Second_H",
        "U_Second_L",
        "U_Zulu",
    ]
    assert [message.get(f) for f in fields] == [ord(d) for d in date[1:]]


def test_parse_invalid_utctime() -> None:
    message = ASN1["UTCTime"]
    invalid = [
        ("860923175628X", 'no "Z" prefix'),
        ("221323175628Z", "month too large #1"),
        ("222023175628Z", "month too large #2"),
        ("229923175628Z", "month too large #3"),
        ("220023175628Z", "month too small"),
        ("220832175628Z", "day too large"),
        ("221000175628Z", "day too small"),
        ("220815255628Z", "hour too large"),
        ("220815176028Z", "minute too large #1"),
        ("220815177028Z", "minute too large #2"),
        ("220815179928Z", "minute too large #3"),
        ("220815173060Z", "second too large #1"),
        ("220815173061Z", "second too large #2"),
        ("220815173999Z", "second too large #3"),
    ]
    for i, m in invalid:
        with pytest.raises(ValueError):
            print(f"{m}: {i}")
            message.parse(i.encode("ascii"))


def test_parse_generalizedtime() -> None:
    message = ASN1["GeneralizedTime"]
    date = chr(15) + "18860923175628Z"
    message.parse(date.encode("ascii"))
    fields = [
        "G_Century_H",
        "G_Century_L",
        "G_Year_H",
        "G_Year_L",
        "G_Month_H",
        "G_Month_L",
        "G_Day_H",
        "G_Day_L",
        "G_Hour_H",
        "G_Hour_L",
        "G_Minute_H",
        "G_Minute_L",
        "G_Second_H",
        "G_Second_L",
        "G_Zulu",
    ]
    assert [message.get(f) for f in fields] == [ord(d) for d in date[1:]]


def test_parse_invalid_generalizedtime() -> None:
    message = ASN1["GeneralizedTime"]
    invalid = [
        ("21860923175628X", 'no "Z" prefix'),
        ("21221323175628Z", "month too large #1"),
        ("21222023175628Z", "month too large #2"),
        ("21229923175628Z", "month too large #3"),
        ("21220023175628Z", "month too small"),
        ("21220832175628Z", "day too large"),
        ("21221000175628Z", "day too small"),
        ("21220815255628Z", "hour too large"),
        ("21220815176028Z", "minute too large #1"),
        ("21220815177028Z", "minute too large #2"),
        ("21220815179928Z", "minute too large #3"),
        ("21220815173060Z", "second too large #1"),
        ("21220815173061Z", "second too large #2"),
        ("21220815173999Z", "second too large #3"),
    ]
    for i, m in invalid:
        with pytest.raises(ValueError):
            i = chr(13) + i
            print(f"{m}: {i}")
            message.parse(i.encode("ascii"))


def test_parse_utctime_message() -> None:
    message = ASN1["UTCTime"]
    date = "860923175628Z"
    message.parse(bytes([len(date)]) + date.encode("ascii"))
    fields = [
        "U_Year_H",
        "U_Year_L",
        "U_Month_H",
        "U_Month_L",
        "U_Day_H",
        "U_Day_L",
        "U_Hour_H",
        "U_Hour_L",
        "U_Minute_H",
        "U_Minute_L",
        "U_Second_H",
        "U_Second_L",
        "U_Zulu",
    ]
    assert [message.get(f) for f in fields] == [ord(d) for d in date]


def test_parse_utctime_message2() -> None:
    message = ASN1["UTCTime"]
    data = bytes(
        [0x0D, 0x31, 0x39, 0x31, 0x32, 0x31, 0x36, 0x30, 0x33, 0x30, 0x32, 0x31, 0x30, 0x5A]
    )
    message.parse(data)
    assert message.get("U_Year_H") == ord("1")
    assert message.get("U_Year_L") == ord("9")
    assert message.get("U_Month_H") == ord("1")
    assert message.get("U_Month_L") == ord("2")
    assert message.get("U_Day_H") == ord("1")
    assert message.get("U_Day_L") == ord("6")
    assert message.get("U_Hour_H") == ord("0")
    assert message.get("U_Hour_L") == ord("3")
    assert message.get("U_Minute_H") == ord("0")
    assert message.get("U_Minute_L") == ord("2")
    assert message.get("U_Second_H") == ord("1")
    assert message.get("U_Second_L") == ord("0")
    assert message.get("U_Zulu") == ord("Z")


def test_parse_generalizedtime_message() -> None:
    message = ASN1["GeneralizedTime"]
    date = "15860923175628Z"
    message.parse(bytes([len(date)]) + date.encode("ascii"))
    fields = [
        "G_Century_H",
        "G_Century_L",
        "G_Year_H",
        "G_Year_L",
        "G_Month_H",
        "G_Month_L",
        "G_Day_H",
        "G_Day_L",
        "G_Hour_H",
        "G_Hour_L",
        "G_Minute_H",
        "G_Minute_L",
        "G_Second_H",
        "G_Second_L",
        "G_Zulu",
    ]
    assert [message.get(f) for f in fields] == [ord(d) for d in date]


def test_parse_strings() -> None:
    def assert_string(message: MessageValue, encoding: str, expected: str) -> None:
        value = message.get("Value")
        assert isinstance(value, bytes)
        assert value == expected.encode(encoding)

    message = ASN1["PrintableString"]

    message.parse(bytes([0x02, 0x68, 0x69]))
    assert_string(message, "ascii", "hi")

    message = ASN1["UTF8String"]

    message.parse(bytes([0x02, 0x68, 0x69]))
    assert_string(message, "ascii", "hi")

    message.parse(bytes([0x04, 0xF0, 0x9F, 0x98, 0x8E]))
    assert_string(message, "utf-8", "😎")


def test_parse_boolean() -> None:
    message = ASN1["BOOL"]
    message.parse(bytes([1, 0]))
    assert message.get("Value") == "B_FALSE"
    message.parse(bytes([1, 0xFF]))
    assert message.get("Value") == "B_TRUE"
    with pytest.raises(ValueError):
        message.parse(bytes([1, 0x14]))
