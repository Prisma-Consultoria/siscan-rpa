import importlib


def get_class_from_module(module_name: str, class_name: str):
    """
    Importa dinamicamente qualquer classe (ou atributo) a partir do nome do módulo e nome da classe/atributo.
    """
    try:
        module = importlib.import_module(module_name)
        attr = getattr(module, class_name, None)
        if attr is None:
            raise ImportError(f"'{class_name}' não encontrado no módulo '{module_name}'")
        return attr
    except Exception as e:
        raise ImportError(f"Falha ao importar '{class_name}' do módulo '{module_name}': {e}") from e
