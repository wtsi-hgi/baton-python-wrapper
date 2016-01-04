from baton._baton_mappers import BatonRunner, BatonCustomObjectMapper


class StubBatonRunner(BatonRunner):
    """
    Stub `BatonRunner`.
    """
    pass


class StubBatonCustomObjectMapper(BatonCustomObjectMapper[dict]):
    """
    Stub `BatonCustomObjectMapper`.
    """
    def _object_serialiser(self, object_as_json: dict) -> dict:
        return object_as_json
