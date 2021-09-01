from typing import List


def calc_sum(arg1: List[float], arg2: List[float]) -> float:
    """Calculate sum of two argments"""
    return sum(arg1) + sum(arg2)


def process_one(arg1: List[float], arg2: List[float]) -> float:
    """Use calc_sum function ones in process"""
    sum_of_args = calc_sum(arg1=arg1, arg2=arg2)

    return sum_of_args


def process_two(arg1: List[float], arg2: List[float], arg3:List[float], arg4:List[float]) -> (float, float):
    """Use calc_sum function twice in process"""
    sum_of_args = calc_sum(arg1=arg1, arg2=arg2)
    sum_of_args2 = calc_sum(arg1=arg3, arg2=arg4)

    return sum_of_args, sum_of_args2
