from typing import List


class MyClass:
    def _summarize(self, contents: List[float]) -> float:
        # 1. 型チェック
        assert isinstance(contents, list)

        # 2. 要素を一つずつ足しあわせていく実装
        sum_number = 0
        for value in contents:
            sum_number += value

        # 3. 型変換
        sum_number = float(sum_number)

        return sum_number

    def summarize(self, contents: List[float]) -> float:
        return self._summarize(contents)
