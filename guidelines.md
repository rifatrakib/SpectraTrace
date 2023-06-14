### Guidelines to test using cURL

* Health Check:
```
curl -X 'GET' \
  'http://127.0.0.1:8000/health' \
  -H 'accept: application/json'
```


##### Security

* Register a user:
```
curl -X 'POST' \
  'http://127.0.0.1:8000/auth/signup' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=username&email=address%40email.com&password=Password%4012345&repeatPassword=Password%4012345'
```
The username must be at least 5 characters, password should have at least 8 characters including at least 1 uppercase, 1 lowercase, 1 special character, and 1 numeric digit. The username and the email, both, should be unique. The response will be something like this:
```
{
  "loc": null,
  "msg": "Account created. Activate your account using http://127.0.0.1:8000/auth/activate?key=<some-unique-key>.",
  "type": null
}
```
sending a request to the link will activate the user account. Note that the link expires in one minute.

* Activate a user account:
```
curl -X 'GET' \
  'http://127.0.0.1:8000/auth/activate?key=<unique-key-obtained-after-signup>' \
  -H 'accept: application/json'
```
This request will activate the user account. Please replace the value of the query parameter `key` with the right value obtained in the response from the response of `/auth/signup`. If the time has exceeded 1 minute, then this request will fail with a 410, in that case, the email used for signup can be used to obtain another unique key.

* Resend activation link:
```
curl -X 'POST' \
  'http://127.0.0.1:8000/auth/activate/resend' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'email=address%40email.com'
```
In case of expiration of the previous activation link, making this request will provide another link with the same amount of expiration (1 minute). Please use the link obtained to activate the account, which should be something like this:
```
{
  "loc": null,
  "msg": "Activation key resent. Activate your account using http://127.0.0.1:8000/auth/activate?key=<new-unique-key>.",
  "type": null
}
```
Use the link contained in the string value of `msg` to activate the account. Note that the link expires after 1 minute.

* Login: After activating the account,
```
curl -X 'POST' \
  'http://127.0.0.1:8000/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=username&password=Password%4012345'
```
This will provide a response like this:
```
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXJuYW1lIiwiZW1haWwiOiJhZGRyZXNzQGVtYWlsLmNvbSIsImlkIjoyLCJpc19hY3RpdmUiOnRydWUsImV4cCI6MTY4NjcwNjM0OSwic3ViIjoic3ViIn0.4GEz9GXwHbaXjTLJHwY2E6U72JpkbjVjGluL9m2_2ew",
  "token_type": "Bearer"
}
```
This response can then be used to create the `Authorization` header in this manner: `Bearer <value of access_token>`, for example in this case, `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXJuYW1lIiwiZW1haWwiOiJhZGRyZXNzQGVtYWlsLmNvbSIsImlkIjoyLCJpc19hY3RpdmUiOnRydWUsImV4cCI6MTY4NjcwNjM0OSwic3ViIjoic3ViIn0.4GEz9GXwHbaXjTLJHwY2E6U72JpkbjVjGluL9m2_2ew`. Please include this in the `Authorization` header for protected endpoints.


##### Audit log

* Get user access key:
```
curl -X 'GET' \
  'http://127.0.0.1:8000/users/access-key/me' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXJuYW1lIiwiZW1haWwiOiJhZGRyZXNzQGVtYWlsLmNvbSIsImlkIjoyLCJpc19hY3RpdmUiOnRydWUsImV4cCI6MTY4NjcwNjM4Miwic3ViIjoic3ViIn0.bi6alk_zBZevVwN1DM6QWGPcoJO1yvsUDsxIAfalxmw'
```
This is a protected endpoint and require the `Authorization` header. This will respond with the unique access key of the logged in user, and this key will be used in the `api-key` header of the `/audit/log` endpoint to send an audit log request to be stored.

* Log an audit event:
```
curl -X 'POST' \
  'http://127.0.0.1:8000/audit/log' \
  -H 'accept: */*' \
  -H 'api-key: 14b36dba-c16e-4174-8494-b234c4bc5dda' \
  -H 'Content-Type: application/json' \
  -d '{
  "category": "event_name",
  "source_information": {
    "application": "app_name",
    "environment": "staging"
  },
  "method": "POST",
  "status": "success",
  "level": "info",
  "event": {
    "name": "Login",
    "type": "Authentication",
    "total_duration": 0.1,
    "affected_resources": 1,
    "latency": 0.05,
    "cpu_usage": 0.5,
    "memory_usage": 0.2,
    "detail": {
      "username": "johndoe"
    },
    "description": "User logged in successfully"
  },
  "actor": {
    "origin": "127.0.0.1",
    "detail": {
      "username": "johndoe"
    }
  },
  "resource": {
    "id": "1",
    "name": "User",
    "type": "User",
    "detail": {
      "username": "johndoe"
    }
  },
  "metadata": [
    {
      "is_metric": true,
      "name": "login_time",
      "value": 0.1
    }
  ]
}'
```
Please note that the `api-key` header must be present in this request and the value must be the same as the `access_key` of the user. This acts as a security measure and also as an identifier for which bucket to use to log the event. So, the `access_key` **must be kept as a secret by the user**.

The body of the request should follow a certain format:

1. There must be a key `category` having a string value with no space.
2. There must be a key `source_information` having a nested object containing a string value at the key `application` and another string at the key `environment`, both must have no spaces in the value.
3. There must be values present in the 3 keys, `method`, `status`, and `level`.
4. There must be a key called `event` containing a nested object, and the nested object must have values at keys: `name`, `type`, `total_duration`, `affected_resources`, `latency`, `cpu_usage`, and `memory_usage`. The `name` and `type` should be string, `affected_resources` should contain an integer stating a count of resources on which the event was performed, the remaining should be float. There can be another optional field called `description` containing a string value, and if any additional data needs to be provided for the event, put that inside the key called `detail`.
5. There must be a key called `actor` which need to contain a nested object with one mandatory key called `origin`, and if any extra data is to be provided, that can be placed under the key `detail`.
6. There can be an optional key called `resource`, and if present, it should contain a nested object with 4 optional keys - `id`, `name`, and `type` having string values, and `detail` which can contain any additional data about the resource.
7. If any extra data needs to be provided with the audit log record, that should be placed inside `metadata` which should contain an array of objects where each object has 3 keys: `is_metric`, `name`, `value`. If `is_metric` is *true*, then that will be stored as an independent field in InfluxDB. `name` should contain the identifying key of the additional data provided, and the `value` should contain the corresponding value.

**The body can also be an array of events following the same format as just mentioned.**

* Log retrieval:
```
curl -X 'GET' \
  'http://127.0.0.1:8000/audit/log?page=1&category=event_name&app=app_name&env=staging&method=POST&status=success&origin=127.0.0.1&start=1d&stop=now%28%29' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXJuYW1lIiwiZW1haWwiOiJhZGRyZXNzQGVtYWlsLmNvbSIsImlkIjoyLCJpc19hY3RpdmUiOnRydWUsImV4cCI6MTY4NjcwNjM4Miwic3ViIjoic3ViIn0.bi6alk_zBZevVwN1DM6QWGPcoJO1yvsUDsxIAfalxmw'
```
This is a protected endpoint, the user must be logged in. Apart from the `category` and the `app` query parameters in this endpoint are optional, and a few have default values - *page* defaults to `1`, *start* defaults to `1d` and *stop* defaults to `now()`.

* Trail of events:
```
curl -X 'GET' \
  'http://127.0.0.1:8000/audit/log/22a8fd00-179c-4045-b716-0c4f6070ad3c' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXJuYW1lIiwiZW1haWwiOiJhZGRyZXNzQGVtYWlsLmNvbSIsImlkIjoyLCJpc19hY3RpdmUiOnRydWUsImV4cCI6MTY4NjcxMDY2Miwic3ViIjoic3ViIn0.KzmtfE04-mveNgmgGHH9snLcSAw1bjYY4cK7ZI67WXM'
```
This endpoint expects an `event_id` as path parameter, this is automatically generated and if a series of events are emitted together, then each will have the same `event_id`. The response will show the events in that series in the descending order of time.

* List of metrics:
```
curl -X 'GET' \
  'http://127.0.0.1:8000/audit/metrics' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXJuYW1lIiwiZW1haWwiOiJhZGRyZXNzQGVtYWlsLmNvbSIsImlkIjoyLCJpc19hY3RpdmUiOnRydWUsImV4cCI6MTY4NjcxMDY2Miwic3ViIjoic3ViIn0.KzmtfE04-mveNgmgGHH9snLcSAw1bjYY4cK7ZI67WXM'
```
This endpoint returns a list of strings where each string is a name for a metric. These names can be used in the metric calculation endpoints.

* Metric calculation:
```
curl -X 'GET' \
  'http://127.0.0.1:8000/audit/metrics/cpu_usage?interval=1m&agg=sum&group_by=status&category=event_name&app=app_name&env=staging&method=POST&status=success&origin=127.0.0.1&start=1d&stop=now%28%29' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXJuYW1lIiwiZW1haWwiOiJhZGRyZXNzQGVtYWlsLmNvbSIsImlkIjoyLCJpc19hY3RpdmUiOnRydWUsImV4cCI6MTY4NjcxMDY2Miwic3ViIjoic3ViIn0.KzmtfE04-mveNgmgGHH9snLcSAw1bjYY4cK7ZI67WXM'
```
This is a protected endpoint, the user must be logged in. Apart from the `category` and the `app` query parameters in this endpoint are optional, and a few have default values - *interval* defaults to `1m` (1 minute), `agg` defaults to `mean`, `group_by` defaults to *null*, *start* defaults to `1d` and *stop* defaults to `now()`. The endpoint must have an `metric_name` obtained from the list of metrics as a path parameter.

* Count metric calculation:
```
curl -X 'GET' \
  'http://127.0.0.1:8000/audit/metrics/status/count?interval=1m&category=event_name&app=app_name&env=staging&method=POST&status=success&origin=127.0.0.1&start=1d&stop=now%28%29' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXJuYW1lIiwiZW1haWwiOiJhZGRyZXNzQGVtYWlsLmNvbSIsImlkIjoyLCJpc19hY3RpdmUiOnRydWUsImV4cCI6MTY4NjcxMDY2Miwic3ViIjoic3ViIn0.KzmtfE04-mveNgmgGHH9snLcSAw1bjYY4cK7ZI67WXM'
```
This is a protected endpoint, the user must be logged in. Apart from the `category` and the `app` query parameters in this endpoint are optional, and a few have default values - *interval* defaults to `1m` (1 minute), *start* defaults to `1d` and *stop* defaults to `now()`. The endpoint must have an `metric_name` which should match any of the categorical fields from the event data format.


##### Additional

* Change password:
```
curl -X 'PATCH' \
  'http://127.0.0.1:8000/auth/password/change' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXJuYW1lIiwiZW1haWwiOiJhZGRyZXNzQGVtYWlsLmNvbSIsImlkIjoyLCJpc19hY3RpdmUiOnRydWUsImV4cCI6MTY4NjcxMDY2Miwic3ViIjoic3ViIn0.KzmtfE04-mveNgmgGHH9snLcSAw1bjYY4cK7ZI67WXM'
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'password=Password%4012345&newPassword=Password%401234&repeatPassword=Password%401234'
```

* Reset password request:
```
curl -X 'POST' \
  'http://127.0.0.1:8000/auth/password/forgot' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'email=admin%40spectratrace.io'
```
The response will be something like mentioned before, there will be an `msg` key which will contain a temporary URL containing a temporary code. Use that code to perform reset password. Note that the link expires in one minute.

* Reset password:
```
curl -X 'PATCH' \
  'http://127.0.0.1:8000/auth/password/reset?key=fb347dae-522d-406d-b1d3-34c5e0580d88' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'newPassword=Admin%4012345&repeatPassword=Admin%4012345'
```
The query parameter key should contain the unique key obtained from the previous reset password request.

* Logged-in user data:
```
curl -X 'GET' \
  'http://127.0.0.1:8000/users/me' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXJuYW1lIiwiZW1haWwiOiJhZGRyZXNzQGVtYWlsLmNvbSIsImlkIjoyLCJpc19hY3RpdmUiOnRydWUsImV4cCI6MTY4NjcxMDY2Miwic3ViIjoic3ViIn0.KzmtfE04-mveNgmgGHH9snLcSAw1bjYY4cK7ZI67WXM'
```
Retrieves data about the logged in user.

* Query user by ID:
```
curl -X 'GET' \
  'http://127.0.0.1:8000/users/1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXJuYW1lIiwiZW1haWwiOiJhZGRyZXNzQGVtYWlsLmNvbSIsImlkIjoyLCJpc19hY3RpdmUiOnRydWUsImV4cCI6MTY4NjcxMDY2Miwic3ViIjoic3ViIn0.KzmtfE04-mveNgmgGHH9snLcSAw1bjYY4cK7ZI67WXM'
```
Passing `user_id` as path parameter like this will return data about the user having the corresponding *user_id*.
