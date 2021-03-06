# Generated by Django 2.2.13 on 2020-11-25 14:53

from django.db import migrations


def make_unique_api_endpoint(apps, schemas):
    DesignRuleTestSuite = apps.get_model("design_rules.DesignRuleTestSuite")

    seen_endpoints = {}
    for test_suite in DesignRuleTestSuite.objects.all():
        if test_suite.api_endpoint in seen_endpoints.keys():
            old_endpoint = test_suite.api_endpoint
            test_suite.api_endpoint = test_suite.api_endpoint + "/" + str(seen_endpoints[test_suite.api_endpoint])
            test_suite.save()
            seen_endpoints[old_endpoint] += 1
        else:
            seen_endpoints[test_suite.api_endpoint] = 1


class Migration(migrations.Migration):

    dependencies = [
        ('design_rules', '0020_auto_20201118_1528'),
    ]

    operations = [
        migrations.RunPython(make_unique_api_endpoint)
    ]
