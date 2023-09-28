import re

from django.http import JsonResponse, HttpResponseServerError, HttpResponse
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit

from . import helper


def determining_login_type(input_string):
    phone_pattern = r'^\+[0-9]+$'
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if re.match(phone_pattern, input_string):
        return 'phone'
    elif re.match(email_pattern, input_string):
        return 'email'
    else:
        return 'username'


def ratelimited(request, exception):
    return HttpResponse(status=429)


@ratelimit(key='ip', rate='5/h')
@ratelimit(key='get:username', rate='1/h')
@require_http_methods(["GET", "POST"])
def register(request):
    if request.GET.get('username', None) is None \
            or request.GET.get('password', None) is None \
            or request.GET.get('contact', None) is None:
        return JsonResponse({
            'status': 'Refused',
            'reason': 'BadRequest',
            'description': 'LackOfArguments'
        }, status=406)

    if not helper.validator.validate_name(request.GET['username']):
        return JsonResponse({
            'status': 'Refused',
            'reason': 'BadRequest',
            'description': 'BadName'
        }, status=400)

    if not helper.validator.validate_password(request.GET['password']):
        return JsonResponse({
            'status': 'Refused',
            'reason': 'BadRequest',
            'description': 'BadPassword'
        }, status=400)

    if helper.validator.CheckAvailability.username(request.GET['username']):
        return JsonResponse({
            'status': 'Refused',
            'reason': 'BadRequest',
            'description': 'UsernameAlreadyRegistered'
        }, status=409)

    contact_type = determining_login_type(request.GET['contact'])

    match contact_type:
        case 'email':
            if helper.validator.CheckAvailability.email(request.GET['contact']):
                return JsonResponse({
                    'status': 'Refused',
                    'reason': 'BadRequest',
                    'description': 'ContactAlreadyRegistered'
                }, status=409)
        case 'phone':
            if helper.validator.CheckAvailability.phone(request.GET['contact']):
                return JsonResponse({
                    'status': 'Refused',
                    'reason': 'BadRequest',
                    'description': 'ContactAlreadyRegistered'
                }, status=409)
        case _:
            return JsonResponse({
                'status': 'Refused',
                'reason': 'BadRequest',
                'description': 'NotValidContact'
            }, status=400)

    id = helper.DBOperator.register(
        request.GET['username'],
        request.GET['password'],
        **{contact_type: request.GET['contact']}
    )

    if id is None:
        return HttpResponseServerError()

    response = {
        'status': 'Done',
        'user-data': {
            'name': request.GET['username'],
            'id': id
        }
    }

    if not (request.method == 'POST' and request.POST.get('create_token', 'false') == 'false'):
        response['auth-data'] = {
            'id': id,
            'token': helper.DBOperator.create_token(request.META.get('HTTP_USER_AGENT'), id)
        }

    return JsonResponse(response, status=200)


@ratelimit(key='ip', rate='5/15m')
@ratelimit(key='get:username', rate='5/12h')
@require_http_methods(["GET"])
def auth(request):
    if request.GET.get('username', None) is None \
            or request.GET.get('password') is None:
        return JsonResponse({
            'status': 'Refused',
            'reason': 'BadRequest',
            'description': 'LackOfArguments'
        }, status=406)

    id = helper.DBOperator.get_id(request.GET['username'])

    if id is None:
        return JsonResponse({
            'status': 'Refused',
            'reason': 'BadRequest',
            'description': 'UserNotFound'
        }, status=404)

    if not helper.DBOperator.auth(determining_login_type(request.GET['username']), request.GET['username'], request.GET['password']):
        return JsonResponse({
            'status': 'Refused',
            'reason': 'BadRequest',
            'description': 'UserNotFound'
        }, status=404)

    return JsonResponse({
        'status': 'Done',
        'auth-data': {
            'id': id,
            'token': helper.DBOperator.create_token(request.META.get('HTTP_USER_AGENT'), id)
        }
    }, status=200)


@ratelimit(key='ip', rate='5/12h')
@ratelimit(key='get:id', rate='3/h')
@require_http_methods(['GET'])
def check_token(request):
    if request.GET.get('id', 0) == 0 or request.GET.get('token', 'NULL') == 'NULL':
        return JsonResponse({
            'status': 'Refused',
            'reason': 'BadRequest',
            'description': 'AuthorizationDenied'
        }, status=406)

    try:
        result = helper.DBOperator.auth_token(int(request.GET['id']), request.GET['token'])
    except ValueError:
        return HttpResponse(status=400)

    return JsonResponse({
        'status': 'Done',
        'reulst': result
    }, status=200)


@require_http_methods(['DELETE', 'GET'])
def control_tokens(request):
    # if not helper.DBOperator.auth_token(request.GET.get('id', 0), request.GET.get('token', 'NULL')):
    #     return JsonResponse({
    #         'status': 'Refused',
    #         'reason': 'BadRequest',
    #         'description': 'AuthorizationDenied'
    #     }, status=403)

    return HttpResponse(status=503)


@require_http_methods(['DELETE', 'GET'])
def control_ttokens(request):
    return HttpResponse(status=503)


class Confirmation:
    @staticmethod
    def email(request):
        pass
