from zds_client import ClientAuth

def get_jwt(object):
    return ClientAuth(
        client_id=object.client_id,
        secret=object.secret,
        # scopes=['zds.scopes.zaken.lezen',
        #         'zds.scopes.zaaktypes.lezen',
        #         'zds.scopes.zaken.aanmaken',
        #         'zds.scopes.statussen.toevoegen',
        #         'zds.scopes.zaken.bijwerken'],
        # zaaktypes=['*']
    )
