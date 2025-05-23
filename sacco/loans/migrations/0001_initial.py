# Generated by Django 5.1.5 on 2025-01-31 07:44

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoanHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change_type', models.CharField(choices=[('approved', 'Approved'), ('rejected', 'Rejected'), ('paid', 'Paid')], max_length=50)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LoanPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('payment_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='LoanRequirement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_mandatory', models.BooleanField(default=True)),
                ('document_required', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='LoanType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('interest_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('min_amount', models.DecimalField(decimal_places=2, default=1000.0, max_digits=15)),
                ('max_amount', models.DecimalField(decimal_places=2, default=100000.0, max_digits=15)),
                ('max_duration_months', models.PositiveIntegerField(default=12)),
            ],
        ),
        migrations.CreateModel(
            name='UserLoanRequirement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_fulfilled', models.BooleanField(default=False)),
                ('document', models.FileField(blank=True, null=True, upload_to='requirements/')),
                ('submitted_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_requested', models.DecimalField(decimal_places=2, max_digits=15)),
                ('amount_approved', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('interest_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('date_requested', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_approved', models.DateTimeField(blank=True, null=True)),
                ('due_date', models.DateField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('repaid', 'Repaid')], default='pending', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('amount_disbursed', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('date_disbursed', models.DateTimeField(blank=True, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loans', to='accounts.account')),
            ],
        ),
    ]
