/**
 * Helper function to get the correct API path based on baseURL
 * 
 * When baseURL is a full HTTPS URL, we need to include /api prefix
 * When baseURL is relative /api, the prefix is already included
 */
export function getApiPath(baseURL: string | undefined, endpoint: string): string {
  // If baseURL is a full URL (starts with http:// or https://), add /api prefix
  if (baseURL?.startsWith('http')) {
    // Ensure endpoint starts with /api
    return endpoint.startsWith('/api') ? endpoint : `/api${endpoint}`;
  }
  // If baseURL is relative (/api), use endpoint as-is
  return endpoint;
}

