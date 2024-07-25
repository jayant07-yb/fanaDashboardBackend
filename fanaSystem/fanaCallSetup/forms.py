from django import forms

class SetupForm(forms.Form):
    table_id = forms.CharField(label='Table ID', max_length=100)
    wifi_name = forms.CharField(label='Wi-Fi Name', max_length=100)
    wifi_password = forms.CharField(label='Wi-Fi Password', widget=forms.PasswordInput)
    port = forms.CharField(label='COM Port', max_length=10)
