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


def create_operand(max_range: int) -> Fraction:
    """
    [cite_start]创建一个数值操作数（自然数或真分数） [cite: 9, 10]。
    数值的范围由max_range控制。

    Args:
        max_range: 数值的最大范围（不包含自身）。

    Returns:
        一个代表操作数的Fraction对象。
    """
    # 随机选择生成自然数还是真分数
    if random.choice([True, False]):
        # 生成一个0到max_range-1之间的自然数
        return Fraction(random.randint(0, max_range - 1))
    else:
        # 生成一个真分数，其分母在[2, max_range-1]范围内
        denominator = random.randint(2, max_range - 1)
        # 分子必须小于分母
        numerator = random.randint(1, denominator - 1)
        return Fraction(numerator, denominator)


def evaluate_expression(expression) -> Fraction:
    """
    递归计算表达式树的值。
    表达式树是一个嵌套元组，例如：((Fraction(1), '+', Fraction(2)), '*', Fraction(3))

    Args:
        expression: 表达式树。

    Returns:
        计算结果，一个Fraction对象。
    """
    # 递归的基准情况：如果节点是数字，直接返回它
    if isinstance(expression, Fraction):
        return expression

    # 递归步骤：分别计算左子树和右子树的值
    left_val = evaluate_expression(expression[0])
    right_val = evaluate_expression(expression[2])
    op = expression[1]  # 获取操作符

    # 根据操作符进行计算
    if op == '+':
        return left_val + right_val
    if op == '-':
        return left_val - right_val
    if op == '×':
        return left_val * right_val
    if op == '÷':
        # 除数不为0已经在生成时保证
        return left_val / right_val