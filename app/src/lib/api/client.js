/**
 * Core API Client
 * 
 * Production-grade HTTP client with:
 * - Error handling
 * - Request/response interceptors
 * - Timeout handling
 * - Logging (development)
 * 
 * All requests go through Next.js middleware (/api/*), not directly to FastAPI
 */

/**
 * @typedef {Object} APIError
 * @property {string} message
 * @property {number} status
 * @property {any} [data]
 */

/**
 * Custom API Error class
 */
export class APIError extends Error {
  constructor(message, status, data) {
    super(message)
    this.name = 'APIError'
    this.status = status
    this.data = data
  }
}

/**
 * Default configuration
 */
const DEFAULT_CONFIG = {
  baseURL: '/api', // Next.js API routes (middleware)
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
}

/**
 * Create fetch request with timeout
 * @param {string} url
 * @param {RequestInit} options
 * @param {number} timeout
 * @returns {Promise<Response>}
 */
async function fetchWithTimeout(url, options = {}, timeout = DEFAULT_CONFIG.timeout) {
  const controller = new AbortController()
  const id = setTimeout(() => controller.abort(), timeout)

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    })
    clearTimeout(id)
    return response
  } catch (error) {
    clearTimeout(id)
    if (error.name === 'AbortError') {
      throw new APIError('Request timeout', 408)
    }
    throw error
  }
}

/**
 * Handle API response
 * @param {Response} response
 * @returns {Promise<any>}
 */
async function handleResponse(response) {
  const contentType = response.headers.get('content-type')
  const isJSON = contentType && contentType.includes('application/json')

  if (!response.ok) {
    const errorData = isJSON ? await response.json().catch(() => ({})) : {}
    const message = errorData.error || errorData.message || `HTTP ${response.status}`
    
    throw new APIError(message, response.status, errorData)
  }

  if (isJSON) {
    return response.json()
  }

  return response.text()
}

/**
 * Core API client class
 */
class APIClient {
  constructor(config = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config }
  }

  /**
   * Build full URL
   * @param {string} path
   * @returns {string}
   */
  buildURL(path) {
    return `${this.config.baseURL}${path}`
  }

  /**
   * Log request (development only)
   * @param {string} method
   * @param {string} url
   * @param {any} [data]
   */
  logRequest(method, url, data) {
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API Client] ${method} ${url}`, data || '')
    }
  }

  /**
   * GET request
   * @param {string} path
   * @param {Object} [params] - Query parameters
   * @returns {Promise<any>}
   */
  async get(path, params = {}) {
    const url = new URL(this.buildURL(path), window.location.origin)
    
    // Add query parameters
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.set(key, String(value))
      }
    })

    this.logRequest('GET', url.pathname + url.search)

    const response = await fetchWithTimeout(
      url.toString(),
      {
        method: 'GET',
        headers: this.config.headers,
      },
      this.config.timeout
    )

    return handleResponse(response)
  }

  /**
   * POST request
   * @param {string} path
   * @param {any} data - Request body
   * @returns {Promise<any>}
   */
  async post(path, data = {}) {
    const url = this.buildURL(path)
    this.logRequest('POST', path, data)

    const response = await fetchWithTimeout(
      url,
      {
        method: 'POST',
        headers: this.config.headers,
        body: JSON.stringify(data),
      },
      this.config.timeout
    )

    return handleResponse(response)
  }

  /**
   * DELETE request
   * @param {string} path
   * @param {Object} [params] - Query parameters
   * @returns {Promise<any>}
   */
  async delete(path, params = {}) {
    const url = new URL(this.buildURL(path), window.location.origin)
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.set(key, String(value))
      }
    })

    this.logRequest('DELETE', url.pathname + url.search)

    const response = await fetchWithTimeout(
      url.toString(),
      {
        method: 'DELETE',
        headers: this.config.headers,
      },
      this.config.timeout
    )

    return handleResponse(response)
  }
}

/**
 * Singleton API client instance
 */
export const apiClient = new APIClient()

/**
 * Export for testing/custom instances
 */
export default APIClient
