ROLES = (
    ('ADMIN', 'ADMIN'),
    ('CLIENT', 'CLIENT'),
)
STATUT = (
    ('CANCEL', 'CANCEL'),
    ('PROGRESS', 'PROGRESS'),
    ('WAIT', 'WAIT'),
    ('FINISH', 'FINISH'),
    ('SUCESS', 'SUCESS'),
)
USER = 'USER'
BANK = 'BANK'
TYPE = (
    ('USER', 'USER'),
    ('BANK', 'BANK'),
)
API_MSG_CODE_CREAT_BANK = 'MG022'


def reponses_generale(msg_code, sucess, results=None, error_code=None, error_msg=None):
    RESPONSE_MSG = {
        'msg_code': msg_code,
        'sucess': sucess,
    }
    if results:
        RESPONSE_MSG.update(
            {'results': results}
        )
    if error_code:
        RESPONSE_MSG.update(
            {'errors': [{'error_code': error_code, 'error_msg': error_msg}]}
        )

    return RESPONSE_MSG
