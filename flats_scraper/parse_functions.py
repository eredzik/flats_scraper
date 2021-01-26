import re
from datetime import datetime


def get_number_from_string(string):
    return float("".join(re.findall(r'(\d*,?\d+)', string)).replace(",", "."))


def parse_olx_time(dt_string):
    str_to_month = {"stycznia": 1,
                    "lutego": 2,
                    "marca": 3,
                    "kwietnia": 4,
                    "maja": 5,
                    "czerwca": 6,
                    "lipca": 7,
                    "sierpnia": 8,
                    "września": 9,
                    "października": 10,
                    "listopada": 11,
                    "grudnia": 12}
    hour, minute, day, month, year = re.findall(
        r".*(\d{1,2}):(\d{1,2}).\s(\d{1,2})\s(\w+)\s(\d{4})", dt_string)[0]
    return datetime(
        int(year),
        str_to_month[month],
        int(day),
        hour=int(hour),
        minute=int(minute))


def parse_mmm_yyyy(string):
    str_to_month = {"sty": 1,
                    "lut": 2,
                    "mar": 3,
                    "kwi": 4,
                    "maj": 5,
                    "cze": 6,
                    "lip": 7,
                    "sie": 8,
                    "wrz": 9,
                    "paź": 10,
                    "lis": 11,
                    "gru": 12}
    month, year = re.findall(r'(\w+)\s(\d{4})', string)[0]
    return datetime(int(year), str_to_month[month], 1, 0, 0, 0)
