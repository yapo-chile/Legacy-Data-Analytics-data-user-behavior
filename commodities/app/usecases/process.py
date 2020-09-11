# pylint: disable=no-member
# utf-8
import logging
from utils.read_params import ReadParams
from usecases.get_commodities import Commodities



class Process(Commodities):
    def __init__(self,
                 config,
                 params: ReadParams,
                 logger) -> None:
        self.config = config
        self.params = params
        self.logger = logger

    def generate(self):
        self.get_commodities()
