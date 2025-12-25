import axios from 'axios'

// Create axios instance with backend URL
const apiBaseURL = import.meta.env.VITE_API_BASE_URL || '/api'

const api = axios.create({
  baseURL: apiBaseURL,
  withCredentials: true, // cookies
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => Promise.reject(error),
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 || error.response?.status === 422) {
      localStorage.removeItem('currentUser')
      localStorage.removeItem('userRole')
    }
    return Promise.reject(error)
  },
)

// ========================================
// OFFER LETTER API FUNCTIONS
// ========================================

/**
 * Fetch eligible candidates for a company
 * These are candidates who have completed interviews with "selected" status
 * @param {number} companyId - Company ID
 * @returns {Promise} Response with candidates list
 */
export const getEligibleCandidates = async (companyId) => {
  try {
    const response = await api.get(`/offer/eligible/${companyId}`)
    return response
  } catch (error) {
    console.error('Error fetching eligible candidates:', error)
    throw error
  }
}

/**
 * Send offer letter to a candidate
 * @param {number} applicationId - Application ID
 * @param {Object} offerData - Optional offer details
 * @param {string} offerData.salary - Annual CTC
 * @param {string} offerData.position - Job position/title
 * @param {string} offerData.start_date - Start date (YYYY-MM-DD)
 * @param {string} offerData.department - Department name
 * @param {string} offerData.work_mode - Remote/Hybrid/On-site
 * @param {string} offerData.benefits - Additional benefits
 * @param {string} offerData.valid_until - Offer validity date
 * @returns {Promise} Response with send status
 */
export const sendOfferLetter = async (applicationId, offerData = {}) => {
  try {
    const response = await api.post(`/offer/send_offer/${applicationId}`, offerData)
    return response.data
  } catch (error) {
    console.error('Error sending offer letter:', error)
    throw error
  }
}

/**
 * Get offer acceptance rate for a company
 * @param {number} companyId - Company ID
 * @returns {Promise} Response with acceptance rate
 */
export const getOfferAcceptanceRate = async (companyId) => {
  try {
    const response = await api.get(`/offer/acceptance_rate/${companyId}`)
    return response.data
  } catch (error) {
    console.error('Error fetching acceptance rate:', error)
    throw error
  }
}

/**
 * Get offer letter status for an application
 * @param {number} applicationId - Application ID
 * @returns {Promise} Response with offer status
 */
export const getOfferStatus = async (applicationId) => {
  try {
    const response = await api.get(`/offer/status/${applicationId}`)
    return response.data
  } catch (error) {
    console.error('Error fetching offer status:', error)
    throw error
  }
}

/**
 * Bulk send offer letters to multiple candidates
 * @param {Array} applicationIds - Array of Application IDs
 * @returns {Promise} Response with bulk send results
 */
export const sendBulkOfferLetters = async (applicationIds) => {
  try {
    const response = await api.post('/offer/send_bulk', {
      application_ids: applicationIds
    })
    return response.data
  } catch (error) {
    console.error('Error sending bulk offer letters:', error)
    throw error
  }
}

// ========================================
// EMAIL STATUS TRACKING HELPERS
// ========================================

/**
 * Track email sending status in local storage
 * @param {number} applicationId - Application ID
 * @param {string} status - 'success' | 'error' | 'sending'
 */
export const trackEmailStatus = (applicationId, status) => {
  const key = `offer_email_status_${applicationId}`
  const statusData = {
    status,
    timestamp: new Date().toISOString()
  }
  localStorage.setItem(key, JSON.stringify(statusData))
}

/**
 * Get email status from local storage
 * @param {number} applicationId - Application ID
 * @returns {Object|null} Email status data
 */
export const getEmailStatus = (applicationId) => {
  const key = `offer_email_status_${applicationId}`
  const stored = localStorage.getItem(key)
  return stored ? JSON.parse(stored) : null
}

/**
 * Clear email status for an application
 * @param {number} applicationId - Application ID
 */
export const clearEmailStatus = (applicationId) => {
  const key = `offer_email_status_${applicationId}`
  localStorage.removeItem(key)
}

/**
 * Clear all email statuses (useful for testing)
 */
export const clearAllEmailStatuses = () => {
  const keys = Object.keys(localStorage)
  keys.forEach(key => {
    if (key.startsWith('offer_email_status_')) {
      localStorage.removeItem(key)
    }
  })
}

/**
 * Convert interview ID to session ID for AI interviews
 * @param {string|number} interviewId - Interview ID (numeric)
 * @returns {Promise} Response with session ID
 */
export const getVideoInterviewSession = async (interviewId) => {
  try {
    const response = await api.get(`/video-interview/interview/${interviewId}/session`)
    return response
  } catch (error) {
    console.error('Error fetching video interview session:', error)
    throw error
  }
}

/**
 * Complete video interview session (generates evaluation.json)
 * @param {string} sessionId - Video interview session ID
 * @returns {Promise} Response with completion status
 */
export const completeVideoInterview = async (sessionId) => {
  try {
    const response = await api.post(`/video-interview/session/${sessionId}/complete`)
    return response
  } catch (error) {
    console.error('Error completing video interview:', error)
    throw error
  }
}

/**
 * Get complete video interview data (evaluation, metadata, transcript)
 * @param {string} sessionId - Video interview session ID
 * @returns {Promise} Response with all interview data
 */
export const getVideoInterviewData = async (sessionId) => {
  try {
    const response = await api.get(`/video-interview/session/${sessionId}/data`)
    return response
  } catch (error) {
    console.error('Error fetching video interview data:', error)
    throw error
  }
}


export default api
