from typing import Iterator, Any, Optional


class StringIteratorIO:
    """
    Class that process large string values.
    """
    def __init__(self, iter_str: Iterator[str]):
        self._iter = iter_str
        self._buff = ''

    def get_large_str(self, n_value: Optional[int] = None) -> str:
        """
        Method that push ib a buffer all string.
        """
        while not self._buff:
            try:
                self._buff = next(self._iter)
            except StopIteration:
                break
        ret = self._buff[:n_value]
        self._buff = self._buff[len(ret):]
        return ret

    def read(self, n_value: Optional[int] = None) -> str:
        """
        Method that parse large string in tokens.
        """
        line = []
        if n_value is None or n_value < 0:
            while True:
                m_value = self.get_large_str()
                if not m_value:
                    break
                line.append(m_value)
        else:
            while n_value > 0:
                m_value = self.get_large_str(n_value)
                if not m_value:
                    break
                n_value -= len(m_value)
                line.append(m_value)
        return ''.join(line)


def clean_csv_value(value: Optional[Any]) -> str:
    """
    Method that clean linebreak from value
    """
    if value is None:
        return r'\N'
    return str(value).replace('\n', '\\n')


def clean_str_value(value: str) -> str:
    """
    Method that clean backslash character from any string.
    """
    return value.replace('\\', '')
