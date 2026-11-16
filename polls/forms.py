from django import forms
from django.core.exceptions import ValidationError

from .models import Poll


class PollCreateForm(forms.Form):
    question = forms.CharField(label="Kararsız kaldığın konu", min_length=5, max_length=200, widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Örn. Bu akşam ne yapsam?"}))
    category = forms.ChoiceField(label="Kategori", choices=Poll.CATEGORY_CHOICES, initial="diger")
    options = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for index in range(5):
            self.fields[f"option_{index}"] = forms.CharField(
                label=f"Seçenek {index + 1}", max_length=80,
                required=index < 2,
                widget=forms.TextInput(attrs={"placeholder": f"Seçenek {index + 1}", "autocomplete": "off"}),
            )

    def clean(self):
        cleaned = super().clean()
        if any(
            name.startswith("option_") and name not in {f"option_{index}" for index in range(5)}
            for name in self.data.keys()
        ):
            raise ValidationError("Bir ankete en fazla 5 seçenek ekleyebilirsin.")
        options = [cleaned.get(f"option_{index}", "").strip() for index in range(5)]
        options = [option for option in options if option]
        if not 2 <= len(options) <= 5:
            raise ValidationError("Anketinde 2 ile 5 arasında seçenek olmalı.")
        if any(len(option) > 80 for option in options):
            raise ValidationError("Seçenekler en fazla 80 karakter olabilir.")
        normalized = [option.casefold() for option in options]
        if len(normalized) != len(set(normalized)):
            raise ValidationError("Aynı seçeneği birden fazla kez ekleyemezsin.")
        cleaned["option_values"] = options
        return cleaned
