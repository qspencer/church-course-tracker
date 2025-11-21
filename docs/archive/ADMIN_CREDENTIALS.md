# Admin Credentials

## Production Admin User

The admin user is created automatically by `backend/create_admin_standalone.py` during container startup.

### Credentials

- **Username**: `Admin` (capital A)
- **Password**: `Admin123!` (with exclamation mark)
- **Email**: `course.tracker.admin@eastgate.church`
- **Role**: `admin`

### Important Notes

1. **Password includes exclamation mark**: The password is `Admin123!` not `Admin123`
2. **Username is case-sensitive**: `Admin` (capital A)
3. **Created automatically**: The admin user is created when the backend container starts
4. **Safe to recreate**: Running the script multiple times will delete and recreate the admin user

### Authentication Endpoint

```bash
POST https://api.quentinspencer.com/api/v1/auth/login
Content-Type: application/json

{
  "username": "Admin",
  "password": "Admin123!"
}
```

### Common Issues

#### 401 Unauthorized Error

**Problem**: Getting 401 error when trying to log in

**Common Causes**:
1. Wrong password (missing exclamation mark)
2. Wrong username (case sensitivity)
3. Admin user not created in database

**Solution**:
- Verify credentials: `Admin` / `Admin123!`
- Check if admin user exists in database
- Re-run admin creation script if needed

#### Password Confusion

**Different scripts use different passwords**:
- `create_admin_standalone.py`: `Admin123!` (used in production)
- `create_default_admin.py`: `Matthew778*` (legacy script)
- Test scripts: Various test passwords

**Always use**: `Admin123!` for production

### Verification

To verify the admin user exists and credentials work:

```bash
# Test login
curl -X POST "https://api.quentinspencer.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"Admin","password":"Admin123!"}'
```

Expected response:
```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

### Security Recommendations

1. **Change default password** after first login
2. **Use strong passwords** for production
3. **Enable MFA** if available
4. **Rotate credentials** regularly
5. **Monitor admin access** in audit logs


