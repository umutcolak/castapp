import abc

from base.base_functions import Base


class PageBase(Base):
    __metaclass__ = abc.ABCMeta  # ADDED

    def __init__(self, driver, explicit_wait=30):
        super().__init__(driver, explicit_wait)
        self.driver = driver

    @abc.abstractmethod
    def check(self):
        raise NotImplementedError("Not implemented yet.")
