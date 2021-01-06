# Add new design rules

To add new design rules please first check the version the api rule needs to be in.

What do we need to do:
1. Add the rule to the choices. (this will allow the rule to be selected in the admin)
2. Add the rule with the needed code to the tasks.
3. Add the task rule to the base task to make sure that it can be executed by a test version.
4. Create tests for the task.
5. Update the base task tests.

##  1. Add the rule to the choices.

Figure out what the version name is. This could be v1 or 07 juli 2020 (dir name: dr_20200709)
Add the version here. In here we fill in the Design rule title, Design rule description and the Design rule url. The first option in ChoiceItem (below "api_03") needs to be unique. Same as the variable name ("api_03_20200709").

dr_20200709.py for API-03
```python
API_03_DESCRIPTION = """The HTTP specification [rfc7231] and the later introduced PATCH method specification [rfc5789] offer a set of standard methods, where every method is designed with explicit semantics. Adhering to the HTTP specification is crucial, since HTTP clients and middleware applications rely on standardized characteristics. Therefore, resources must be retrieved or manipulated using standard HTTP methods."""

api_03_20200709 = ChoiceItem(
    "api_03", _("API-03 V-09-07-2020: Only apply standard HTTP methods"),
    description=API_03_DESCRIPTION, url="https://publicatie.centrumvoorstandaarden.nl/api/adr/#api-03",
)
```

After adding this, we must add it to the choices. They are in the init file.

__init__.py
```
from djchoices import DjangoChoices

from .dr_20200709 import api_03_20200709


class DesignRuleChoices(DjangoChoices):
    # 09-07-2020
    api_03_20200709 = api_03_20200709
```

## 2. Add the rule with the needed code to the tasks.

In the task folder there are folders with the versions in there. Make sure that the version folder is there for the task you would like to add. In there should be an __init__.py file with an import of all the design rules in this version.

name the file after the design rule number like `api_03.py` in here the code needs to be added and the result for the session needs to be created. Just like the code below.

api_57.py
```python
from urllib.parse import urlparse

import semver

from django.utils.translation import ugettext_lazy as _

from ...choices import DesignRuleChoices


def run_20200709_api_57(session, response):
    """
    https://publicatie.centrumvoorstandaarden.nl/api/adr/#api-57
    """
    from ...models import DesignRuleResult

    # We do not want double results for the same design rule
    base_qs = session.results.filter(rule_type=DesignRuleChoices.api_57_20200709)
    if base_qs.exists():
        return base_qs.first()

    result = DesignRuleResult(design_rule=session, rule_type=DesignRuleChoices.api_57_20200709)

    if "API-Version" not in response.headers:
        result.success = False
        result.errors = [_("The headers is missing. Make sure that the 'API-Version' is given.")]
    else:
        result.success = True
    result.save()
    return result
```

Also don't forget to add your task to the `__init__.py` file of your version.

## 3. Add the task rule to the base task to make sure that it can be executed by a test version.

The next thing that needs to be done is that the task needs to be called. This will happen in the `base.py` file in tasks. In here there is a forloop that will call all the rules that are assigned to the test verion. Add your task here.

```python
for test_option in session.test_version.test_rules.all():
    if test_option.rule_type == DesignRuleChoices.api_03_20200709:
        result = run_20200709_api_03(session=session)
        if result.success:
            success_count += 1
```

## 4. Create tests for the task.

Make sure that everything in your task is tested. So we minimize bugs.

## 5. Update the base task tests.

This is to make sure that the rule can be run.
