# NinjaRMM API Integration

Complete integration with NinjaRMM (comda.rmmservice.eu) using OAuth 2.0 authentication.

## 📋 Overview

This repository contains multiple implementations for connecting to the NinjaRMM API:

- **ninja-api.html** - Web-based interface with visual UI
- **ninja-api.py** - Python script for API calls
- **ninja-api.js** - Node.js script for API calls
- **ninja-api-test.py** - Quick test script

## 🔐 Current Credentials

- **Client ID**: `FLFI6ANM2S7MG4AEOTA5`
- **Client Secret**: `47jn6gqcb6r402g48hmblcepcb642a5e553dempl`
- **Base URL**: `https://comda.rmmservice.eu`

## ⚠️ Important Notice

The current credentials return a "Client app not exist" error. This means you need to create an OAuth Client App in your NinjaRMM admin panel first.

## 🚀 Setting Up OAuth Client App

To use the API, you must create OAuth credentials in NinjaRMM:

### Step 1: Access API Settings

1. Log in to NinjaRMM at: https://comda.rmmservice.eu/auth/#/login
2. Navigate to: **Administration** → **Apps** → **API**
3. Click on **Client App IDs** section

### Step 2: Create New Client App

1. Click **"Add"** or **"Create New Client App"**
2. Fill in the details:
   - **Name**: API Integration
   - **Description**: OAuth client for API access
   - **Redirect URI**: `http://localhost` (or your callback URL)
   - **Scopes**: Select:
     - ✅ Monitoring
     - ✅ Management
     - ✅ Read
     - ✅ Write (if needed)

3. Click **Save**

### Step 3: Get Your Credentials

After creating the app, you'll receive:
- **Client ID** (like: FLFI6ANM2S7MG4AEOTA5)
- **Client Secret** (like: 47jn6gqcb6r402g48hmblcepcb642a5e553dempl)

Update these credentials in all the scripts.

## 📝 Usage

### Option 1: Web Interface (Recommended for Testing)

1. Open `ninja-api.html` in a web browser
2. Click "Get Access Token"
3. Select an API endpoint from the dropdown
4. Click "Call API Endpoint"
5. View results in the response panel

### Option 2: Python Script

```bash
# Install dependencies
pip install requests

# Run the script
python3 ninja-api.py
```

### Option 3: Node.js Script

```bash
# Run the script (no dependencies needed)
node ninja-api.js
```

### Option 4: Quick Test

```bash
# Test authentication only
python3 ninja-api-test.py
```

## 🔌 Available API Endpoints

Once authenticated, you can access:

- `/v2/organizations` - Get all organizations
- `/v2/devices` - Get all devices/endpoints
- `/v2/device-roles` - Get device role configurations
- `/v2/activities` - Get recent activities
- `/v2/queries` - Get saved queries
- `/v2/alerts` - Get alerts
- `/v2/policies` - Get policies

## 🛠️ Authentication Flow

The scripts use OAuth 2.0 Client Credentials flow:

1. **Request Token**:
   ```
   POST https://comda.rmmservice.eu/ws/oauth/token
   Content-Type: application/x-www-form-urlencoded

   grant_type=client_credentials
   &client_id=YOUR_CLIENT_ID
   &client_secret=YOUR_CLIENT_SECRET
   &scope=monitoring management
   ```

2. **Receive Token**:
   ```json
   {
     "access_token": "eyJhbGc...",
     "token_type": "Bearer",
     "expires_in": 3600
   }
   ```

3. **Use Token**:
   ```
   GET https://comda.rmmservice.eu/v2/organizations
   Authorization: Bearer eyJhbGc...
   Content-Type: application/json
   ```

## 📊 Example Response

```json
{
  "organizations": [
    {
      "id": 1,
      "name": "My Organization",
      "description": "Primary organization",
      "nodeApprovalMode": "AUTOMATIC"
    }
  ]
}
```

## 🔍 Troubleshooting

### "Client app not exist" Error

**Cause**: OAuth client credentials haven't been created in NinjaRMM.

**Solution**: Follow the "Setting Up OAuth Client App" steps above.

### Authentication Fails

1. Verify credentials are correct
2. Check if the client app is enabled
3. Ensure scopes include "monitoring" and "management"
4. Verify the base URL is `https://comda.rmmservice.eu`

### CORS Errors (Web Interface)

The HTML interface may encounter CORS issues when running locally. Solutions:

1. Use the Python or Node.js scripts instead
2. Run the HTML through a local server
3. Set up a proxy server

### API Call Returns 401

**Cause**: Token expired or invalid.

**Solution**: Request a new access token. Tokens typically expire after 1 hour.

### API Call Returns 403

**Cause**: Insufficient permissions.

**Solution**: Check OAuth scopes and user permissions in NinjaRMM.

## 📚 API Documentation

Official NinjaRMM API documentation:
- https://app.ninjarmm.com/apidocs/
- https://eu.ninjarmm.com/apidocs-beta/

## 🔒 Security Best Practices

1. **Never commit credentials** to version control
2. Use environment variables for production:
   ```bash
   export NINJA_CLIENT_ID="your_client_id"
   export NINJA_CLIENT_SECRET="your_client_secret"
   ```
3. Rotate credentials regularly
4. Use minimal required scopes
5. Implement token refresh logic for long-running applications
6. Store tokens securely (encrypted)

## 📦 Files in This Repository

| File | Purpose |
|------|---------|
| `ninja-api.html` | Interactive web interface for API testing |
| `ninja-api.py` | Python script with full API integration |
| `ninja-api.js` | Node.js script with full API integration |
| `ninja-api-test.py` | Quick authentication test |
| `ninja-api-finder.py` | Region finder (for standard instances) |
| `NINJA_API_README.md` | This documentation file |

## 🎯 Next Steps

1. ✅ Create OAuth client app in NinjaRMM admin panel
2. ✅ Update credentials in the scripts
3. ✅ Test authentication with `ninja-api-test.py`
4. ✅ Explore API endpoints with the web interface
5. ✅ Integrate into your application

## 📞 Support

For NinjaRMM API questions:
- Email: [email protected]
- Documentation: https://app.ninjarmm.com/apidocs/

## 📄 License

These integration scripts are provided as-is for educational and development purposes.
