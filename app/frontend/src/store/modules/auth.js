// src/store/modules/auth.js
import api from '@/services/api'

export default {
  namespaced: true,

  state: {
    // persisted user (raw object returned from API + normalized fields)
    currentUser: JSON.parse(localStorage.getItem('currentUser')) || null,
    // convenience: stored company id (for HR/org)
    companyId: localStorage.getItem('companyId') || null,
    isAuthenticated: !!JSON.parse(localStorage.getItem('currentUser')),
    userRole: localStorage.getItem('userRole') || null,
    authError: null,
    loading: false,
  },

  mutations: {
    setUser(state, userData) {
      state.currentUser = userData || null
      state.isAuthenticated = !!userData
      state.userRole = userData?.role || null
      state.companyId = userData?.company_id || null

      // persist minimal useful info
      localStorage.setItem('currentUser', JSON.stringify(userData || null))
      localStorage.setItem('userRole', userData?.role || '')
      localStorage.setItem('companyId', userData?.company_id ? String(userData.company_id) : '')
    },

    clearUser(state) {
      state.currentUser = null
      state.companyId = null
      state.isAuthenticated = false
      state.userRole = null
      localStorage.removeItem('currentUser')
      localStorage.removeItem('userRole')
      localStorage.removeItem('companyId')
    },

    setAuthError(state, error) {
      state.authError = error
      state.loading = false
    },

    clearAuthError(state) {
      state.authError = null
    },

    setLoading(state, loading) {
      state.loading = loading
    },
  },

  actions: {
    // simple health check helper (optional)
    async checkBackendStatus({ commit }) {
      try {
        const r = await api.get('/health')
        return { success: true, data: r.data }
      } catch (e) {
        return { success: false, error: e.message || e }
      }
    },

    // Register (keeps original semantics; backend handles role inference by email)
    async registerUser({ commit }, userData) {
      commit('setLoading', true)
      commit('clearAuthError')

      try {
        // Minimal validation
        if (!userData || !userData.email || !userData.password || !userData.name) {
          const msg = 'Name, email and password are required'
          commit('setAuthError', msg)
          return { success: false, error: msg }
        }

        const payload = {
          name: userData.name,
          email: userData.email,
          password: userData.password,
          phone: userData.phone || '',
          role: userData.role || undefined,
          company_name: userData.company_name || undefined,
          cin: userData.cin || undefined,
        }

        const res = await api.post('/auth/register', payload)
        // registration may set cookies; return response
        commit('clearAuthError')
        return { success: true, data: res.data }
      } catch (err) {
        const msg = err.response?.data?.message || err.message || 'Registration failed'
        commit('setAuthError', msg)
        return { success: false, error: msg }
      } finally {
        commit('setLoading', false)
      }
    },

    // LOGIN: core area — normalize response, then if HR role lacks company_id, fetch /hr/<hr_id>
    async loginUser({ commit }, credentials) {
      commit('setLoading', true)
      commit('clearAuthError')

      if (!credentials || !credentials.email || !credentials.password) {
        const msg = 'Email and password are required'
        commit('setAuthError', msg)
        commit('setLoading', false)
        return { success: false, error: msg }
      }

      try {
        const res = await api.post('/auth/login', {
          email: credentials.email,
          password: credentials.password,
        })

        const raw = res.data || {}

        // remove any unnecessary message field
        if (raw.message) delete raw.message

        // normalize main user object with common ids
        const user = {
          // id: prefer applicant_id, then hr_id, then company_id (organization)
          id: raw.applicant_id || raw.hr_id || raw.company_id || null,
          applicant_id: raw.applicant_id || null,
          hr_id: raw.hr_id || null,
          company_id: raw.company_id || null, // may be null for hr on your backend
          role: raw.role || null,
          email: credentials.email,
          name: raw.name || credentials.email.split('@')[0],
          // include any other returned fields
          ...raw,
        }

        // Defensive step: if role is 'hr' and backend didn't give company_id, fetch /hr/<hr_id>
        if (user.role === 'hr' && user.hr_id && !user.company_id) {
          try {
            const hrRes = await api.get(`/hr/${user.hr_id}`)
            const hrData = hrRes?.data || {}

            // hr endpoint might return camelCase or snake_case; try both
            const companyIdFromHr = hrData.company_id ?? hrData.companyId ?? null

            if (companyIdFromHr) {
              user.company_id = companyIdFromHr
            } else {
              // fallback: maybe hrData contains nested company object
              const nestedCompanyId =
                (hrData.company && (hrData.company.id || hrData.company.company_id)) ||
                (hrData.company_info && (hrData.company_info.id || hrData.company_info.company_id)) ||
                null
              if (nestedCompanyId) user.company_id = nestedCompanyId
            }
          } catch (e) {
            // don't fail login if this fetch fails; just warn and continue
            // console.warn kept intentionally — helps debugging
             
            console.warn('Could not fetch HR profile to obtain company_id:', e)
          }
        }

        // If role is 'admin' / 'organization' your backend may already return company_id; keep it.
        // Commit normalized user to store (and localStorage)
        commit('setUser', user)
        commit('clearAuthError')
        return { success: true, data: user }
      } catch (err) {
        const msg = err.response?.data?.message || err.message || 'Login failed'
        commit('setAuthError', msg)
        return { success: false, error: msg }
      } finally {
        commit('setLoading', false)
      }
    },

    // Logout: call backend then clear state/cookies
    async logout({ commit }) {
      try {
        await api.post('/auth/logout')
      } catch (e) {
        // ignore network errors for logout - still clear locally
         
        console.warn('Logout API error (ignored):', e)
      }
      commit('clearUser')
      return { success: true }
    },
  },

  getters: {
    currentUser: (s) => s.currentUser,
    companyId: (s) => s.companyId,
    isAuthenticated: (s) => s.isAuthenticated,
    userRole: (s) => s.userRole,
    isHR: (s) => s.userRole === 'hr',
    isApplicant: (s) => s.userRole === 'applicant',
    isOrganization: (s) => s.userRole === 'organization' || s.userRole === 'admin',
    authError: (s) => s.authError,
    loading: (s) => s.loading,
  },
}
