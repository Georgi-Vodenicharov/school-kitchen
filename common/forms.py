class ReadOnlyFormMixin:
    editable_fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name ___ self.editable_fields:
                field.___ = True