from django import forms
from services.models import Service, ServiceCategory
from .models import Order, OrderItem
from django import forms
from .models import Order


class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['deadline', 'status', 'manager']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }


class OrderCreateForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=ServiceCategory.objects.all(),
        label="Paslaugų kategorija"
    )
    service = forms.ModelChoiceField(
        queryset=Service.objects.none(),
        label="Paslauga"
    )
    quantity = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=1,
        label="Kiekis"
    )

    class Meta:
        model = Order
        fields = ['deadline']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pradžioje paslaugų nėra — jos bus užpildytos AJAX
        self.fields['service'].queryset = Service.objects.none()
