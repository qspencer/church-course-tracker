# User API 500 Reproduction

- Endpoint: `POST https://api.quentinspencer.com/api/v1/users/`
- Payload example:
  ```json
  {
    "username": "autotest5894",
    "email": "autotest5894@example.com",
    "full_name": "Automation Test",
    "password": "Automation123",
    "role": "staff",
    "is_active": true
  }
  ```
- Response: `500 Internal Server Error`
- Headers: includes `apigw-requestid: TwokGh95oAMEZlg=`
- Admin token used: retrieved via `Admin/Admin123!`

`PUT /users/97` with updated password also returns 500.

Next steps: backend to inspect CloudWatch logs for request id above.
