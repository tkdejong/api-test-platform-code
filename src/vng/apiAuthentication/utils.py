def create_token(token_model, user, serializer):
    tokens = token_model.objects.filter(user=user)
    if not tokens:
        token = token_model.objects.create(user=user, name='api_token')
    else:
        token = tokens.last()
    return token
