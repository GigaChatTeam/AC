# GigaChat server point for authentication / registration
HTTP point written with Python and Django 

***

# API

**Registration**

Entry point

* GET/POST `http://<?>/register`

Arguments

* GET
* * `username` - desired user name
* * `password` - desired account password
* * `contact` - user's email/phone number
* POST (not implemented)
* * `username` - desired user name
* * `password` - desired account password
* * `contact` - user's email/phone number
* * `create_token` - whether to generate a token. By default, false. If a string other than `false` is supplied, then true.

Returning (JSON)

* GET | 200
* * `status`: str - `Done`
* * `auth-data`
* * * `id`: int - id of the created user
* * * `token`: str - full account access token
* * `user-data`
* * * `id`: int - id of the created user
* * * `name`: str - name of the created user
* GET | 400
* * `status`: str - `Refused`
* * `reason`: str - `BadRequest`
* * `description`: str - `LackOfArgument`/`BadName`/`BadPassword`/`NotValidContact`
* GET | 409
* * `status`: str - `Refused`
* * `reason`: str - `BadRequest`
* * `description`: str - `UsernameAlreadyRegistered`/`ContactAlreadyRegistered`

**Authorization**

Entry point

* GET `http://<?>/auth`

Arguments

* GET
* * `username` - username/email/phone number of the account
* * `password` - account password

Returning (JSON)

* GET | 200
* * `status`: str - `Done`
* * `auth-data`
* * * `id`: int - id of the created user
* * * `token`: str - full account access token
* GET | 400
* * `status`: str - `Refused`
* * `reason`: str - `BadRequest`
* * `description`: str - `LackOfArgument`
* GET | 404
* * `status`: str - `Refused`
* * `reason`: str - `BadRequest`
* * `description`: str - `UserNotFound`