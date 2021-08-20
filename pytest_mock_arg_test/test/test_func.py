from unittest.mock import MagicMock, call, patch

from src.func import process_one


@patch("src.func.calc_sum")
def test_process_one(mocked_calc_sum: MagicMock):
    actual = process_one(arg1=[0.1, 0.2], arg2=[0.3, 0.4])
    actual_args = mocked_calc_sum.call_args
    print(actual_args)
    print(type(actual_args[0]))
    print(actual_args[0])
    print(type(actual_args[1]))
    print(actual_args[1])


#
# @patch("src.func.calc_sum")
# def test_process_two(mocked_calc_sum: MagicMock):
#     actual = process_two(arg1=[0.1, 0.2], arg2=[0.3, 0.4], arg3=[0.5, 0.6], arg4=[0.7, 0.8])
#     actual_args = mocked_calc_sum.call_args_list
#     print(actual_args)
#     print(type(actual_args[0]))
#     print(actual_args[0][1])
#     print(type(actual_args[1]))
#     print(actual_args[1])
