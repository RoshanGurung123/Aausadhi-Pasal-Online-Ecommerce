from django import forms
from .models import Account


class RegistrationForm(forms.ModelForm):
    # creating password field
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Enter password'}))
    
    #creating confirm password field
    confirm_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Confirm password'}))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name',
                  'phone_number', 'email', 'password']
    
    def clean(self):
        cleaned_data=super(RegistrationForm,self).clean()
        password=cleaned_data.get('password')
        confirm_password=cleaned_data.get('confirm_password')
    # using super to do with our requirement and modifying things

        if password !=confirm_password:
            raise forms.ValidationError('Password does not match!!')

    # assigning css to all the fields 
    def __init__(self,* args, **kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder']='Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder']='Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder']='Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder']='Enter Your Email Address'

        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'
    
    # throwing the error message to the user if the password doesn't match
