# GigaChat server point for authentication / registration

***

# API

## Registration

Entry point

* `POST` -> `http://<?>/register`

`POST` parameters take precedence over `GET` parameters

Methods - `POST`

Arguments

* `POST` arguments
* * `username` - desired user name
* * `password` - desired account password
* * `contact` - user's email/phone number
* `GET` arguments
* * `username` - desired user name
* * !`password` - not applicable
* * `contact` - user's email/phone number

Returning (JSON)

* `POST` | 200
* * `status`: STRING - `Done`
* * `data`
* * * `id`: INT64 - id of the created user
* * * `username`: STRING - name of the created user
* * * `token`: STRING - full account access token

* `POST` | 400
* * `status`: STRING - `Refused`
* * `reason`: STRING - `BadRequest`
* * `description`: STRING - `BadName`/`BadPassword`/`NotValidContact`
* `POST` | 406
* * `status`: STRING - `Refused`
* * `reason`: STRING - `BadRequest`
* * `description`: STRING - `UnsafeHandling`/`LackOfArgument`
* `POST` | 409
* * `status`: STRING - `Refused`
* * `reason`: STRING - `BadRequest`
* * `description`: STRING - `UsernameAlreadyRegistered`/`ContactAlreadyRegistered`

## Authorization

Entry point

* `POST` -> `http://<?>/auth`

`POST` parameters take precedence over `GET` parameters

Methods - `POST`

Arguments

* `POST` arguments
* * `username` - login username
* * `password` - login password
* `GET` arguments
* * `username` - login username
* * !`password` - not applicable

Returning (JSON)

* `POST` | 200
* * `status`: STRING - `Done`
* * `data`
* * * `id`: INT64 - ID of specified user
* * * `username`: STRING - specified username
* * * `token`: STRING - full account access token
* `POST` | 404
* * `status`: STRING - `Refused`
* * `reason`: STRING - `BadRequest`
* * `description`: STRING - 'UserNotFound'
* `POST` | 406
* * `status`: STRING - `Refused`
* * `reason`: STRING - `BadRequest`
* * `description`: STRING - `UnsafeHandling`/`LackOfArgument`
