/**
 * Helper function to get the correct API path based on baseURL
 * 
 * When baseURL is a full HTTPS URL, we need to include /api prefix
 * (baseURL is always a full URL now - no relative paths)
 */
export function getApiPath(baseURL: string | undefined, endpoint: string): string {
  // baseURL is always a full URL (http:// or https://)
  // We need to ensure the endpoint includes the /api prefix
  if (baseURL?.startsWith('http')) {
    // Ensure endpoint starts with /api
    return endpoint.startsWith('/api') ? endpoint : `/api${endpoint}`;
  }
  // Fallback: if baseURL is somehow not a full URL, still add /api prefix
  return endpoint.startsWith('/api') ? endpoint : `/api${endpoint}`;
}

