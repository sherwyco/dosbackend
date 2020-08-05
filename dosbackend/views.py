from django.shortcuts import HttpResponse
from graphene import Schema

from .schema import Mutation


def verify_account(request, token):
    mutation = ("""mutation {
         verifyAccount(
        token: "%s",
        ) {
            success, errors
            }
        }
    """ % token)
    schema = Schema(mutation=Mutation)
    result = schema.execute(mutation)
    tuple_list = list(result.data.items())
    success = tuple_list[0][1]["success"]
    if success:
        return HttpResponse("<div>Account Successfully Verified!</div>")
    else:
        error = tuple_list[0][1]["errors"]["nonFieldErrors"][0]["message"]
        return HttpResponse("<div>%s</div>" % error)
