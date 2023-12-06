from django.http import JsonResponse, HttpResponseServerError
from django.views.decorators.http import require_http_methods

from . import helper


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

    form['contact_type'] = helper.determining_login_type(form['contact'])

    match form['contact_type']:
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

    user_id = helper.DBOperator.register(
        form['username'],
        form['password'],
        **{form['contact_type']: form['contact']}
    )

    if user_id is None:
        return HttpResponseServerError()

    return JsonResponse({
        'status': 'Done',
        'data': {
            'id': user_id,
            'username': form['username'],
            'token': helper.DBOperator.create_token(request.META.get('HTTP_USER_AGENT'), user_id)
        }
    }, status=200)


@require_http_methods(["POST"])
def auth(request):
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

    user_id = helper.DBOperator.get_id(form['username'])

    if user_id is None:
        return JsonResponse({
            'status': 'Refused',
            'reason': 'BadRequest',
            'description': 'UserNotFound'
        }, status=404)

    if not helper.DBOperator.auth(
            helper.determining_login_type(form['username']),
            form['username'],
            form['password']):
        return JsonResponse({
            'status': 'Refused',
            'reason': 'BadRequest',
            'description': 'UserNotFound'
        }, status=404)

    return JsonResponse({
        'status': 'Done',
        'data': {
            'id': user_id,
            'username': form['username'],
            'token': helper.DBOperator.create_token(request.META.get('HTTP_USER_AGENT'), user_id)
        }
    }, status=200)
