# core/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Category, Tag, Link, Report, Feedback
import csv
import io


class AdminLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class CategoryForm(forms.ModelForm):
    ICON_CHOICES = [
        ('bi-folder', 'Folder'),
        ('bi-bank', 'Bank/Government'),
        ('bi-info-circle', 'Information'),
        ('bi-mortarboard', 'Education'),
        ('bi-heart-pulse', 'Health'),
        ('bi-car-front', 'Vehicle/Transport'),
        ('bi-shield-check', 'Security/Police'),
        ('bi-currency-rupee', 'Finance'),
        ('bi-briefcase', 'Employment'),
        ('bi-house', 'Housing'),
        ('bi-globe', 'Web/Internet'),
        ('bi-telephone', 'Communication'),
        ('bi-lightning', 'Electricity/Utility'),
        ('bi-droplet', 'Water'),
        ('bi-tree', 'Agriculture'),
        ('bi-airplane', 'Travel'),
        ('bi-shop', 'Business'),
        ('bi-person-badge', 'Identity'),
        ('bi-file-earmark-text', 'Documents'),
        ('bi-gear', 'Services'),
        ('bi-people', 'Social'),
        ('bi-truck', 'Logistics'),
        ('bi-book', 'Library/Knowledge'),
        ('bi-newspaper', 'News/Media'),
    ]

    icon = forms.ChoiceField(choices=ICON_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Category
        fields = ['name', 'icon', 'color', 'description', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class LinkForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
    )
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter tags separated by commas (e.g., Government, License, Vehicle)'
        }),
        help_text='Comma separated tags'
    )

    class Meta:
        model = Link
        fields = ['title', 'url', 'description', 'categories', 'is_featured', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['tags_input'].initial = ', '.join(
                self.instance.tags.values_list('name', flat=True)
            )

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            tags_str = self.cleaned_data.get('tags_input', '')
            tag_names = [t.strip() for t in tags_str.split(',') if t.strip()]
            tags = []
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(
                    name__iexact=name,
                    defaults={'name': name}
                )
                tags.append(tag)
            instance.tags.set(tags)
        return instance


class CSVImportForm(forms.Form):
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'}),
        help_text='CSV format: Category, Website Name, URL, Description, Tags (optional)'
    )

    def clean_csv_file(self):
        f = self.cleaned_data['csv_file']
        if not f.name.endswith('.csv'):
            raise forms.ValidationError('File must be a CSV file.')
        return f

    def process_csv(self, user=None):
        f = self.cleaned_data['csv_file']
        decoded = f.read().decode('utf-8')
        reader = csv.reader(io.StringIO(decoded))
        results = {'success': 0, 'errors': [], 'duplicates': 0}

        for i, row in enumerate(reader, 1):
            if len(row) < 4:
                results['errors'].append(f"Row {i}: Not enough columns")
                continue

            cat_names = [c.strip() for c in row[0].split('+')]
            title = row[1].strip()
            url = row[2].strip()
            desc = row[3].strip()
            tag_names = [t.strip() for t in row[4].split(',')] if len(row) > 4 else []

            if Link.objects.filter(url=url).exists():
                results['duplicates'] += 1
                results['errors'].append(f"Row {i}: URL already exists - {url}")
                continue

            try:
                link = Link.objects.create(
                    title=title,
                    url=url,
                    description=desc,
                    created_by=user
                )

                for cname in cat_names:
                    cat, _ = Category.objects.get_or_create(
                        name__iexact=cname,
                        defaults={'name': cname}
                    )
                    link.categories.add(cat)

                for tname in tag_names:
                    if tname:
                        tag, _ = Tag.objects.get_or_create(
                            name__iexact=tname,
                            defaults={'name': tname}
                        )
                        link.tags.add(tag)

                results['success'] += 1
            except Exception as e:
                results['errors'].append(f"Row {i}: {str(e)}")

        return results


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['report_type', 'message', 'email']
        widgets = {
            'report_type': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe the issue...'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email (optional)'}),
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name (optional)'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email (optional)'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Your feedback or suggestion...'}),
        }