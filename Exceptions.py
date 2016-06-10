class Error(Exception):
    """
    Базовый класс для исключений в модуле.
    """
    pass


class LocationNotFoundError(Error):
    def __init__(self, ontology_name, message):
        self.ontology_name = ontology_name
        self.message = message


class KeywordNotFoundError(Error):
    def __init__(self, message):
        self.message = message