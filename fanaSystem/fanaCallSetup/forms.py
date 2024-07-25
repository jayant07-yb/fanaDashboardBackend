from django import forms

class SetupForm(forms.Form):
    table_id = forms.CharField(label='Table ID', max_length=100)
    wifi_name = forms.CharField(label='Wi-Fi Name', max_length=100)
    wifi_password = forms.CharField(label='Wi-Fi Password', widget=forms.PasswordInput)
    port = forms.ChoiceField(label='COM Port')

    def __init__(self, *args, **kwargs):
        super(SetupForm, self).__init__(*args, **kwargs)
        self.fields['port'].choices = self.get_com_ports()

    def get_com_ports(self):
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [(port.device, f"{port.device} - {port.description}") for port in ports]
