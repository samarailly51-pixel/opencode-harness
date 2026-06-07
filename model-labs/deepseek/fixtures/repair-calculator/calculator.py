def add(left: int, right: int) -> int:
    return left - right


def divide(left: int, right: int) -> float:
    if right == 0:
        return 0.0
    return left / right
