import json
from decimal import Decimal, InvalidOperation

from django import forms
from django.utils.translation import gettext_lazy as _

from services.models import ServiceCategory
from .models import Order


class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['deadline', 'status', 'is_paid', 'manager', 'manager_comment']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
            'manager_comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class OrderCreateForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=ServiceCategory.objects.all(),
        required=False,
        label=_("Paslaugų kategorija"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    items_json = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Order
        fields = ['deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean_items_json(self):
        raw = self.cleaned_data.get('items_json', '').strip()
        if not raw:
            raise forms.ValidationError(_("Pridėkite bent vieną paslaugos eilutę."))

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise forms.ValidationError(_("Neteisingas užsakymo eilučių formatas.")) from exc

        if not isinstance(parsed, list) or not parsed:
            raise forms.ValidationError(_("Pridėkite bent vieną paslaugos eilutę."))

        normalized = []
        for row in parsed:
            try:
                service_id = int(row.get('service_id'))
                quantity = Decimal(str(row.get('quantity')))
            except (TypeError, ValueError, InvalidOperation):
                raise forms.ValidationError(_("Neteisingi paslaugos arba kiekio duomenys."))

            if quantity <= 0:
                raise forms.ValidationError(_("Kiekis turi būti didesnis už 0."))

            normalized.append({'service_id': service_id, 'quantity': quantity})

        return normalized
