from djchoices import DjangoChoices, ChoiceItem


class ResultChoices(DjangoChoices):
    success = ChoiceItem("Success")
    failed = ChoiceItem("Failed")
