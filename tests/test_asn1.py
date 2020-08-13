from typing import Generator

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
    data = message.get("Data")
    assert isinstance(data, list)
    assert [d.value for d in data] == [0x6E, 0x5D, 0xC0]


@pytest.mark.skip(reason="ISSUE: Componolit/RecordFlux#")
def test_parse_bit_string_invalid_unused() -> None:
    message = ASN1["Message"]
    with pytest.raises(ValueError):
        message.parse(bytes([0x03, 0x04, 0x06, 0x6E, 0x5D, 0xC1]))


def test_parse_octet_string() -> None:
    message = ASN1["Message"]
    message.parse(bytes([0x04, 0x04, 0x03, 0x02, 0x06, 0xA0]))
    data = message.get("Data")
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
    date = "860923175628Z"
    message.parse(date.encode("ascii"))
    fields = [
        "Year_H",
        "Year_L",
        "Month_H",
        "Month_L",
        "Day_H",
        "Day_L",
        "Hour_H",
        "Hour_L",
        "Minute_H",
        "Minute_L",
        "Second_H",
        "Second_L",
        "Zulu",
    ]
    assert [message.get(f) for f in fields] == [ord(d) for d in date]


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
    date = "18860923175628Z"
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
    assert [message.get(f) for f in fields] == [ord(d) for d in date]


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
            print(f"{m}: {i}")
            message.parse(i.encode("ascii"))


def test_parse_utctime_message() -> None:
    message = ASN1["Message"]
    date = "860923175628Z"
    message.parse(bytes([0x17, len(date)]) + date.encode("ascii"))
    fields = [
        "UTCTime_Year_H",
        "UTCTime_Year_L",
        "UTCTime_Month_H",
        "UTCTime_Month_L",
        "UTCTime_Day_H",
        "UTCTime_Day_L",
        "UTCTime_Hour_H",
        "UTCTime_Hour_L",
        "UTCTime_Minute_H",
        "UTCTime_Minute_L",
        "UTCTime_Second_H",
        "UTCTime_Second_L",
        "UTCTime_Zulu",
    ]
    assert [message.get(f) for f in fields] == [ord(d) for d in date]


def test_parse_generalizedtime_message() -> None:
    message = ASN1["Message"]
    date = "15860923175628Z"
    message.parse(bytes([0x18, len(date)]) + date.encode("ascii"))
    fields = [
        "GeneralizedTime_G_Century_H",
        "GeneralizedTime_G_Century_L",
        "GeneralizedTime_G_Year_H",
        "GeneralizedTime_G_Year_L",
        "GeneralizedTime_G_Month_H",
        "GeneralizedTime_G_Month_L",
        "GeneralizedTime_G_Day_H",
        "GeneralizedTime_G_Day_L",
        "GeneralizedTime_G_Hour_H",
        "GeneralizedTime_G_Hour_L",
        "GeneralizedTime_G_Minute_H",
        "GeneralizedTime_G_Minute_L",
        "GeneralizedTime_G_Second_H",
        "GeneralizedTime_G_Second_L",
        "GeneralizedTime_G_Zulu",
    ]
    assert [message.get(f) for f in fields] == [ord(d) for d in date]
