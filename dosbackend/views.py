from .schema import Mutation, Query
from graphene import Schema, ObjectType
from django.shortcuts import HttpResponse


def verify_account(request, token):
    test = '''mutation {
  verifyAccount(
    token: "%s",
  ) {
    success, errors
  }
}
''' % token
    schema = Schema(mutation=Mutation)
    result = schema.execute(test)
    tuple_list = list(result.data.items())
    success = tuple_list[0][1]['success']
    if success:
        return HttpResponse('<div>SUCCESS!</div>')
    else:
        error = tuple_list[0][1]['errors']['nonFieldErrors'][0]['message']
        return HttpResponse('<div>%s</div>' % error)


