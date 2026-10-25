from django import forms


class ReadOnlyFormMixin:
    editable_fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in self.editable_fields:
                field.disabled = True


class UniqueNameFormMixin:
    duplicate_message = 'Вече съществува запис с име „{name}“.'

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        model = self._meta.model
        duplicates = model.objects.filter(name__iexact=name).exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError(self.duplicate_message.format(name=name))
        return name