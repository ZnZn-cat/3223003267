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


def to_canonical_form(expression) -> str:
    """
    将表达式树转换为唯一的范式字符串以进行查重 。
    对于+和×，子表达式的范式字符串按字典序排序。
    """
    # 基准条件：数值节点直接转换为 "分子/分母" 格式的字符串
    if isinstance(expression, Fraction):
        return str(expression.numerator) + '/' + str(expression.denominator)

    # 递归步骤：获取左右子节点和操作符
    left, op, right = expression

    # 递归地获取左右子树的范式字符串
    left_canonical = to_canonical_form(left)
    right_canonical = to_canonical_form(right)

    # 核心查重逻辑：对于满足交换律的+和×运算符
    if op in ['+', '×']:
        # 将其左右子节点的范式字符串按字典序排序。
        # 这可以保证无论原始顺序是 a+b 还是 b+a，生成的范式都是一样的。
        if left_canonical > right_canonical:
            left_canonical, right_canonical = right_canonical, left_canonical

    # 将处理后的左右范式与操作符组合成当前节点的范式
    return f"({left_canonical}{op}{right_canonical})"


# --- 主要业务逻辑：生成题目和批改 ---

def generate_problems(num_problems: int, max_range: int):
    """
    [cite_start]生成指定数量和范围的题目，并写入文件 [cite: 20, 23, 31, 35]。
    """
    # 检查-r参数的有效性
    if max_range <= 1:
        print("错误: -r 参数值必须大于1。")
        return

    exercises = []  # 用于存放生成的题目字符串
    answers = []  # 用于存放对应的答案字符串
    generated_expressions = set()  # 使用集合存储范式字符串，用于高效查重

    print(f"正在生成 {num_problems} 道题目，请稍候...")
    # 循环直到生成了足够数量的独一无二的题目
    while len(exercises) < num_problems:
        # 每道题目的操作符数量随机为1到3个
        num_ops = random.randint(1, 3)
        expr_tree = generate_expression_tree(num_ops, max_range)

        # 查重: 将生成的表达式树转换为范式字符串
        canonical = to_canonical_form(expr_tree)
        # 检查范式是否存在于集合中，如果存在，则说明题目重复，跳过本次循环
        if canonical in generated_expressions:
            continue

        # 如果是新题目，将其范式添加到集合中，防止后续重复
        generated_expressions.add(canonical)

        # 将表达式树格式化为题目和答案
        question_str = expression_to_string(expr_tree) + " ="
        answer_val = evaluate_expression(expr_tree)
        answer_str = format_fraction(answer_val)

        # 将格式化后的题目和答案添加到列表中
        exercises.append(question_str)
        answers.append(answer_str)

        # 打印进度提示，避免在生成大量题目时程序看起来像卡住了
        if len(exercises) % (num_problems // 10 or 1) == 0:
            print(f"已生成 {len(exercises)} / {num_problems} 道...")

    # 将结果写入文件
    try:
        # 写入题目到Exercises.txt
        with open("Exercises.txt", "w", encoding="utf-8") as f_ex:
            for i, ex in enumerate(exercises):
                f_ex.write(f"{i + 1}. {ex}\n")

        # 写入答案到Answers.txt
        with open("Answers.txt", "w", encoding="utf-8") as f_ans:
            for i, ans in enumerate(answers):
                f_ans.write(f"{i + 1}. {ans}\n")
        print("题目已存入 Exercises.txt")
        print("答案已存入 Answers.txt")

    except IOError as e:
        print(f"文件写入失败: {e}")


def grade_files(exercise_file: str, answer_file: str):
    """
    [cite_start]根据题目文件和答案文件，批改对错并统计数量 [cite: 40, 41]。
    """
    try:
        # 读取题目和答案文件
        with open(exercise_file, 'r', encoding='utf-8') as f_ex:
            questions = [line.strip() for line in f_ex.readlines()]
        with open(answer_file, 'r', encoding='utf-8') as f_ans:
            user_answers = [line.strip() for line in f_ans.readlines()]
    except FileNotFoundError as e:
        print(f"错误：找不到文件 {e.filename}")
        return

    correct_indices = []  # 存放正确的题号
    wrong_indices = []  # 存放错误的题号

    # 定义一个内部函数，用于安全地解析题目字符串并计算结果
    def safe_eval_string(question_str):
        # 将题目中的运算符'÷'和'×'替换为Python可识别的'/'和'*'
        question_str = question_str.replace('÷', '/')
        question_str = question_str.replace('×', '*')
        # 移除题号和等号，得到纯表达式
        question_str = re.sub(r'^\d+\.\s*', '', question_str).replace(' =', '').strip()

        # 定义一个正则表达式替换函数，用于将带分数"a'b/c"转换为Python表达式"(a + Fraction(b, c))"
        def mixed_to_improper(match):
            integer = int(match.group(1))
            numerator = int(match.group(2))
            denominator = int(match.group(3))
            return f"({integer} + Fraction({numerator}, {denominator}))"

        # 应用上面的替换
        question_str = re.sub(r"(\d+)'(\d+)/(\d+)", mixed_to_improper, question_str)

        # 将纯分数"b/c"转换为"Fraction(b,c)"
        question_str = re.sub(r"(\d+)/(\d+)", r"Fraction(\1, \2)", question_str)

        # 使用Python的eval函数执行计算。第二个参数限制了eval内部的可用函数，只允许使用Fraction
        result = eval(question_str, {"Fraction": Fraction})
        return result

    # 遍历每一道题和对应的用户答案
    for i, (q, a) in enumerate(zip(questions, user_answers)):
        q_text = q
        a_text = a.split('. ')[-1]  # 从 "1. 答案" 这样的格式中提取出答案部分

        try:
            # 计算题目的正确答案
            correct_answer_fraction = safe_eval_string(q_text)
            correct_answer_str = format_fraction(correct_answer_fraction)

            # 比较用户答案和正确答案
            if a_text == correct_answer_str:
                correct_indices.append(i + 1)  # 如果正确，记录题号
            else:
                wrong_indices.append(i + 1)  # 如果错误，记录题号

        except Exception as e:
            # 如果在解析或计算过程中发生任何错误，都将该题判为错误
            print(f"处理第 {i + 1} 题时出错: {e}")
            wrong_indices.append(i + 1)

    # [cite_start]将统计结果写入Grade.txt文件 [cite: 42, 43, 44]
    try:
        with open("Grade.txt", "w", encoding="utf-8") as f_grade:
            f_grade.write(f"Correct: {len(correct_indices)} ({','.join(map(str, correct_indices))})\n")
            f_grade.write(f"Wrong: {len(wrong_indices)} ({','.join(map(str, wrong_indices))})\n")
        print("批改结果已存入 Grade.txt")
    except IOError as e:
        print(f"文件写入失败: {e}")


# --- 主程序入口与命令行参数解析 ---

def main():
    """主函数，负责解析命令行参数并调用相应功能"""
    # 初始化参数解析器
    parser = argparse.ArgumentParser(description="小学四则运算题目生成与批改程序")

    # 定义命令行参数
    parser.add_argument("-n", type=int, help="生成题目的个数 [cite: 20]")
    parser.add_argument("-r", type=int, help="题目中数值（自然数、分数分母）的范围 [cite: 23]")
    parser.add_argument("-e", type=str, help="待批改的题目文件路径 ")
    parser.add_argument("-a", type=str, help="对应的答案文件路径 ")

    # 解析从命令行传入的参数
    args = parser.parse_args()

    # 根据参数组合决定程序执行哪种功能
    if args.e and args.a:
        # 如果-e和-a参数都提供了，则执行批改功能
        print("--- 进入批改模式 ---")
        grade_files(args.e, args.a)
    elif args.n and args.r:
        # 如果-n和-r参数都提供了，则执行题目生成功能
        print("--- 进入题目生成模式 ---")
        generate_problems(args.n, args.r)
    else:
        # 其他情况
        # 如果提供了-n但没有提供-r，这是个错误，程序应报错并退出
        if args.n and not args.r:
            parser.error("使用 -n 参数时，必须同时提供 -r 参数。 [cite: 25]")
        # 如果参数组合不匹配任何功能，则打印帮助信息
        else:
            parser.print_help()


# 确保只有当该脚本被直接执行时，main()函数才会被调用
if __name__ == "__main__":
    main()