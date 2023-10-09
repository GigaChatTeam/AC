# GigaChat server point for authentication / registration

***

# API

## Registration

Entry point

* GET/POST `http://<?>/register`

Arguments

* GET
* * `username` - desired user name
* * `password` - desired account password
* * `contact` - user's email/phone number
* POST
* * `username` - desired user name
* * `password` - desired account password
* * `contact` - user's email/phone number
* * `create_token` - whether to generate a token. By default, false. If a string other than `false` is supplied, then true.

Returning (JSON)

* GET | 200
* * `status`: str - `Done`
* * `data`
* * * `id`: int - id of the created user
* * * `token`: str - full account access token
* * `user-data`
* * * `id`: int - id of the created user
* * * `name`: str - name of the created user
* POST | 200
* * `status`: str - `Done`
* * (if required) `data`
* * * `id`: int - id of the created user
* * * `token`: str - full account access token
* * `user-data`
* * * `id`: int - id of the created user
* * * `name`: str - name of the created user
* GET/POST | 400
* * `status`: str - `Refused`
* * `reason`: str - `BadRequest`
* * `description`: str - `LackOfArgument`/`BadName`/`BadPassword`/`NotValidContact`
* GET/POST | 409
* * `status`: str - `Refused`
* * `reason`: str - `BadRequest`
* * `description`: str - `UsernameAlreadyRegistered`/`ContactAlreadyRegistered`
* GET/POST | 500
* * Server error

## Authorization

Entry point

* GET `http://<?>/auth`

Arguments

* GET
* * `username` - username/email/phone number of the account
* * `password` - account password

Returning (JSON)

* GET | 200
* * `status`: str - `Done`
* * `data`
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
* GET/POST | 500
* * Server error


## Token controller

### Verify token

Entry point

* GET `http://<?>/control/tokens/get`

Arguments

* GET
* * `id` - username/email/phone number of the account
* * `token` - account password

Returning (JSON)

* GET | 200
* * `status`: str - `Done`
* * `data`: bool - is there such a working token
* GET | 406
* * `status`: str - `Refused`
* * `reason`: str - `BadRequest`
* * `description`: str - `LackOfArgumentsAuthorization`

### Get tokens info

Entry point

* GET `http://<?>/control/tokens`

Arguments

* GET
* * `id` - username/email/phone number of the account
* * `token` - account password

Returning (JSON)

* GET | 200
* * _Not completed_
* GET | 404
* * `status`: str - `Refused`
* * `reason`: str - `BadRequest`
* * `description`: str - `UserNotFound`
* GET | 406
* * `status`: str - `Refused`
* * `reason`: str - `BadRequest`
* * `description`: str - `LackOfArgumentsAuthorization`

### Delete tokens

Entry point

* DELETE `http://<?>/control/tokens`

Arguments

* GET
* * `id` - username/email/phone number of the account
* * `token` - account password
* * `agent`: optional - which substring should include the name of the token agent
* * `started`: optional - before what date (`%Y-%m-%d-%H:%M:%S`) should the token be created for deletion

Returning (JSON)

* DELETE | 200
* * `status`: str - `Done`
* * `count`: infInt - count of deleted tokens
* DELETE | 404
* * `status`: str - `Refused`
* * `reason`: str - `BadRequest`
* * `description`: str - `UserNotFound`
* DELETE | 406
* * `status`: str - `Refused`
* * `reason`: str - `BadRequest`
* * `description`: str - `LackOfArgumentsAuthorization`