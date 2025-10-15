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


def generate_expression_tree(max_ops: int, max_range: int):
    """
    递归生成一个符合所有约束的表达式树。
    - 树的结构为 (left_child, operator, right_child)
    - 叶子节点为 Fraction 对象

    Args:
        max_ops: 该子树中允许的最大操作符数量。
        max_range: 操作数的数值范围。

    Returns:
        生成的表达式树。
    """
    # 基准情况：如果没有剩余操作符，则返回一个操作数
    if max_ops == 0:
        return create_operand(max_range)

    # 为了生成不同复杂度的表达式，有一定概率提前终止递归，直接生成操作数
    if max_ops > 0 and random.random() < 0.4:
        return create_operand(max_range)

    # 随机选择一个操作符
    ops = ['+', '-', '×', '÷']
    op = random.choice(ops)

    # 随机分配剩余的操作符数量给左、右子树
    remaining_ops = max_ops - 1
    left_ops = random.randint(0, remaining_ops)
    right_ops = remaining_ops - left_ops

    # 循环直到生成一个满足所有条件的有效子树
    while True:
        # 递归生成左右子树
        left_child = generate_expression_tree(left_ops, max_range)
        right_child = generate_expression_tree(right_ops, max_range)

        # 计算左右子树的值，用于检查约束
        left_val = evaluate_expression(left_child)
        right_val = evaluate_expression(right_child)

        # 应用题目约束: 减法结果不能是负数
        if op == '-' and left_val < right_val:
            # 如果不满足条件，则交换左右子节点（这是一个简化处理，也可以选择重新生成）
            left_child, right_child = right_child, left_child
            left_val, right_val = right_val, left_val

        # 应用题目约束: 除法结果必须是真分数
        if op == '÷':
            # 约束1：除数不能为0
            if right_val == 0:
                continue  # 重新生成
            # 约束2：结果是真分数，意味着被除数必须小于除数
            if left_val >= right_val:
                continue  # 重新生成

        # 如果所有约束都满足，返回生成的子树
        return (left_child, op, right_child)


# --- 查重与格式化 ---

def get_precedence(op):
    """获取运算符的优先级，用于决定是否加括号。"""
    if op in ['+', '-']:
        return 1  # 加减法优先级低
    if op in ['×', '÷']:
        return 2  # 乘除法优先级高
    return 0  # 数字没有优先级


def expression_to_string(expression, parent_precedence=0) -> str:
    """
    通过中序遍历将表达式树转换为带必要括号的字符串。

    Args:
        expression: 表达式树。
        parent_precedence: 父节点的运算符优先级。

    Returns:
        格式化后的表达式字符串。
    """
    # 基准情况：如果是操作数，直接格式化并返回
    if isinstance(expression, Fraction):
        return format_fraction(expression)

    # 递归步骤：解构表达式树节点
    left, op, right = expression
    current_precedence = get_precedence(op)

    # 递归转换左右子树为字符串
    left_str = expression_to_string(left, current_precedence)
    right_str = expression_to_string(right, current_precedence)

    # 决定是否需要加括号：
    # 如果当前运算符的优先级低于父运算符，则必须加括号以保证运算顺序。
    # 例如，在 (1+2)*3 中，+ 的优先级低于 *，所以 1+2 需要被括号括起来。
    if current_precedence < parent_precedence:
        return f"({left_str} {op} {right_str})"

    # 默认情况下不加括号
    return f"{left_str} {op} {right_str}"
