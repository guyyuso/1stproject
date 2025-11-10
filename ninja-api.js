#!/usr/bin/env node

/**
 * NinjaRMM API Integration Script
 *
 * This script demonstrates how to:
 * 1. Authenticate with NinjaRMM using OAuth 2.0 Client Credentials
 * 2. Make API calls to retrieve organization and device data
 *
 * Usage: node ninja-api.js
 */

const https = require('https');
const http = require('http');

// Configuration
const config = {
  clientId: 'H9E-VrYBPxfV1_zf17IExUgs_o4',
  clientSecret: 'k-Fv9NbgfT9ZDYkbR-19wHzn1ot2RnU975AfAOo8V-HVB_7PyYRAxg',
  baseUrl: 'comda.rmmservice.eu',
  tokenEndpoint: '/ws/oauth/token',
  apiEndpoints: {
    organizations: '/v2/organizations',
    devices: '/v2/devices',
    deviceRoles: '/v2/device-roles',
    activities: '/v2/activities',
    queries: '/v2/queries'
  }
};

/**
 * Make an HTTPS request
 */
function makeRequest(options, postData = null) {
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          resolve({
            statusCode: res.statusCode,
            headers: res.headers,
            data: jsonData
          });
        } catch (e) {
          resolve({
            statusCode: res.statusCode,
            headers: res.headers,
            data: data
          });
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    if (postData) {
      req.write(postData);
    }

    req.end();
  });
}

/**
 * Get OAuth Access Token
 */
async function getAccessToken() {
  console.log('🔐 Requesting OAuth Access Token...');
  console.log(`   Client ID: ${config.clientId}`);
  console.log(`   Token URL: https://${config.baseUrl}${config.tokenEndpoint}\n`);

  const postData = new URLSearchParams({
    grant_type: 'client_credentials',
    client_id: config.clientId,
    client_secret: config.clientSecret,
    scope: 'monitoring management'
  }).toString();

  const options = {
    hostname: config.baseUrl,
    port: 443,
    path: config.tokenEndpoint,
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Content-Length': Buffer.byteLength(postData)
    }
  };

  try {
    const response = await makeRequest(options, postData);

    if (response.statusCode === 200 && response.data.access_token) {
      console.log('✅ Successfully obtained access token!');
      console.log(`   Token Type: ${response.data.token_type}`);
      console.log(`   Expires In: ${response.data.expires_in} seconds`);
      console.log(`   Access Token: ${response.data.access_token.substring(0, 20)}...`);
      console.log('');
      return response.data.access_token;
    } else {
      console.error('❌ Failed to obtain access token');
      console.error(`   Status Code: ${response.statusCode}`);
      console.error(`   Response: ${JSON.stringify(response.data, null, 2)}`);
      throw new Error(response.data.error_description || response.data.error || 'Authentication failed');
    }
  } catch (error) {
    console.error('❌ Error during authentication:', error.message);
    throw error;
  }
}

/**
 * Call NinjaRMM API Endpoint
 */
async function callApiEndpoint(accessToken, endpoint, endpointName) {
  console.log(`📡 Calling API: ${endpointName}`);
  console.log(`   Endpoint: https://${config.baseUrl}${endpoint}\n`);

  const options = {
    hostname: config.baseUrl,
    port: 443,
    path: endpoint,
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  };

  try {
    const response = await makeRequest(options);

    if (response.statusCode === 200) {
      console.log(`✅ ${endpointName} - Success!`);
      console.log(`   Status: ${response.statusCode}`);
      console.log(`   Response:\n`);
      console.log(JSON.stringify(response.data, null, 2));
      console.log('\n' + '='.repeat(80) + '\n');
      return response.data;
    } else {
      console.error(`❌ ${endpointName} - Failed`);
      console.error(`   Status Code: ${response.statusCode}`);
      console.error(`   Response: ${JSON.stringify(response.data, null, 2)}`);
      console.log('');
    }
  } catch (error) {
    console.error(`❌ Error calling ${endpointName}:`, error.message);
  }
}

/**
 * Main execution
 */
async function main() {
  console.log('╔════════════════════════════════════════════════════════════════╗');
  console.log('║           NinjaRMM API Integration Script                      ║');
  console.log('╚════════════════════════════════════════════════════════════════╝');
  console.log('');

  try {
    // Step 1: Get Access Token
    const accessToken = await getAccessToken();

    // Step 2: Call API Endpoints
    await callApiEndpoint(accessToken, config.apiEndpoints.organizations, 'Get Organizations');
    await callApiEndpoint(accessToken, config.apiEndpoints.devices, 'Get Devices');
    await callApiEndpoint(accessToken, config.apiEndpoints.deviceRoles, 'Get Device Roles');

    console.log('✅ All API calls completed successfully!');
  } catch (error) {
    console.error('\n❌ Script execution failed:', error.message);
    process.exit(1);
  }
}

// Run the script
if (require.main === module) {
  main();
}

module.exports = { getAccessToken, callApiEndpoint, config };
