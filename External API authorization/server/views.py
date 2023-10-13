import re
from datetime import datetime

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
@require_http_methods(["POST"])
def register(request):
    if request.GET.get('password', None) is not None:
        return JsonResponse({
            'status': 'Refused',
            'reason': 'BadRequest',
            'description': 'UnsafeHandling'
        }, status=406)

    form = {
        'username': request.POST.get('username', None) or request.GET.get('username', None),
        'password': request.POST.get('password'),
        'contact': request.POST.get('contact', None) or request.GET.get('contact', None)
    }

    if form['username'] is None or form['password'] is None or form['contact'] is None:
        return JsonResponse({
            'status': 'Refused',
            'reason': 'BadRequest',
            'description': 'LackOfArguments',
            'arguments': [key for key, value in form.items() if value is None]
        }, status=406)

    if not helper.validator.validate_name(form['username']):
        return JsonResponse({
            'status': 'Refused',
            'reason': 'BadRequest',
            'description': 'BadName'
        }, status=400)

    if not helper.validator.validate_password(form['password']):
        return JsonResponse({
            'status': 'Refused',
            'reason': 'BadRequest',
            'description': 'BadPassword'
        }, status=400)

    if helper.validator.CheckAvailability.username(form['username']):
        return JsonResponse({
            'status': 'Refused',
            'reason': 'BadRequest',
            'description': 'UsernameAlreadyRegistered'
        }, status=409)

    form['contact_type'] = determining_login_type(form['contact'])

    match form['contact']:
        case 'email':
            if helper.validator.CheckAvailability.email(form['contact']):
                return JsonResponse({
                    'status': 'Refused',
                    'reason': 'BadRequest',
                    'description': 'ContactAlreadyRegistered'
                }, status=409)
        case 'phone':
            if helper.validator.CheckAvailability.phone(form['contact']):
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
        form['username'],
        form['password'],
        **{form['contact_type']: form['contact']}
    )

    if id is None:
        return HttpResponseServerError()

    return JsonResponse({
        'status': 'Done',
        'data': {
            'id': id,
            'username': form['username'],
            'token': helper.DBOperator.create_token(request.META.get('HTTP_USER_AGENT'), id)
        }
    }, status=200)


@ratelimit(key='ip', rate='5/15m')
@ratelimit(key='get:username', rate='5/12h')
@require_http_methods(["POST"])
def auth(request):
    if request.GET.get('password', None) is not None:
        return JsonResponse({
            'status': 'Refused',
            'reason': 'BadRequest',
            'description': 'UnsafeHandling'
        }, status=406)

    form = {
        'username': request.POST.get('username', None) or request.GET.get('username', None),
        'password': request.POST.get('password')
    }

    if form['username'] is None or form['password'] is None:
        return JsonResponse({
            'status': 'Refused',
            'reason': 'BadRequest',
            'description': 'LackOfArguments',
            'arguments': [key for key, value in form.items() if value is None]
        }, status=406)

    id = helper.DBOperator.get_id(form['username'])

    if id is None:
        return JsonResponse({
            'status': 'Refused',
            'reason': 'BadRequest',
            'description': 'UserNotFound'
        }, status=404)

    if not helper.DBOperator.auth(
            determining_login_type(form['username']),
            request.GET['username'],
            request.GET['password']):
        return JsonResponse({
            'status': 'Refused',
            'reason': 'BadRequest',
            'description': 'UserNotFound'
        }, status=404)

    return JsonResponse({
        'status': 'Done',
        'data': {
            'id': id,
            'username': form['username'],
            'token': helper.DBOperator.create_token(request.META.get('HTTP_USER_AGENT'), id)
        }
    }, status=200)


class TokensController:
    @staticmethod
    @ratelimit(key='ip', rate='24/24h')
    @ratelimit(key='get:id', rate='12/h')
    def check_validity(request):
        if request.GET.get('id', 0) == 0 or request.GET.get('token', 'NULL') == 'NULL':
            return JsonResponse({
                'status': 'Refused',
                'reason': 'BadRequest',
                'description': 'LackOfArgumentsAuthorization'
            }, status=406)

        return JsonResponse({
            'status': 'Done',
            'data': helper.DBOperator.auth_token(request.GET['id'], request.GET['token'])
        })

    @staticmethod
    @require_http_methods(["GET", "DELETE"])
    def control_tokens(request):
        if request.GET.get('id', 0) == 0 or request.GET.get('token', 'NULL') == 'NULL':
            return JsonResponse({
                'status': 'Refused',
                'reason': 'BadRequest',
                'description': 'LackOfArgumentsAuthorization'
            }, status=406)

        if not helper.DBOperator.auth_token(request.GET['id'], request.GET['token']):
            return JsonResponse({
                'status': 'Refused',
                'reason': 'BadRequest',
                'description': 'UserNotFound'
            }, status=404)

        match request.method:
            case 'GET':
                return JsonResponse(helper.DBOperator.TokensControl.get_valid_tokens(int(request.GET['id'])),
                                    safe=False)
            case 'DELETE':
                try:
                    time = datetime.strptime(request.GET.get('started', ''), "%Y-%m-%d-%H:%M:%S")
                except ValueError:
                    time = None

                return JsonResponse({
                    'status': 'Done',
                    'count': helper.DBOperator.TokensControl.revoke_token(
                        request.GET['id'],
                        agent=request.GET.get('agent', None),
                        time=time)
                })
