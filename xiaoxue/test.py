import random
import argparse
from fractions import Fraction
import re
import os


# --- 核心功能：表达式的生成、计算与格式化 ---

def format_fraction(f: Fraction) -> str:
    """
    [cite_start]将Fraction对象格式化为要求的带分数或真分数字符串 [cite: 34, 38]。
    例如：
    - Fraction(3, 1) -> "3"
    - Fraction(2, 5) -> "2/5"
    - Fraction(5, 2) -> "2'1/2"

    Args:
        f: 一个Fraction对象。

    Returns:
        格式化后的字符串。
    """
    # 如果分母是1，说明是自然数，直接返回分子
    if f.denominator == 1:
        return str(f.numerator)

    # 计算整数部分和余数的分子
    integer_part = f.numerator // f.denominator
    remainder_numerator = f.numerator % f.denominator

    # 如果余数为0，说明可以整除，返回整数部分
    if remainder_numerator == 0:
        return str(integer_part)

    # 如果整数部分为0，说明是真分数
    if integer_part == 0:
        return f"{remainder_numerator}/{f.denominator}"
    # 否则，是带分数
    else:
        return f"{integer_part}'{remainder_numerator}/{f.denominator}"