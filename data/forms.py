
from django import forms

class EmailForm(forms.Form):
    email = forms.EmailField(label='Tu correo electrónico', max_length=100)

class PasswordResetForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label='Nueva contraseña')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirmar nueva contraseña')

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data