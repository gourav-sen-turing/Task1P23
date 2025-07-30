from typing import Dict


class GeneratorBase:
    def __init__(self):
        self.custom_types = {}
        self.constraint = False
        self.im_index = False


def generate_model_generator(types_mapping: Dict, templates, prefix: str):
    class ModelGenerator(GeneratorBase):
        def __init__(self):
            self.state = set()
            self.postgresql_dialect_cols = set()
            self.types_mapping = types_mapping
            self.templates = templates
            self.prefix = prefix
            super().__init__()

    return ModelGenerator
