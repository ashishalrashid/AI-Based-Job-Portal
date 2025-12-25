import api from "@/services/api"

export default {
  namespaced: true,

  // -------------------------------------------------------------
  // STATE
  // -------------------------------------------------------------
  state: {
    profile: null,

    // Applications
    applications: [],
    applicationSummary: {},

    // Interviews
    interviews: [],
    interviewSummary: {},

    loading: false,
    error: null,

    // REQUIRED for job detail + apply
    applicant_id: null,
  },

  // -------------------------------------------------------------
  // MUTATIONS
  // -------------------------------------------------------------
  mutations: {
    // PROFILE
    setProfile(state, profile) {
      state.profile = profile
    },

    // APPLICATIONS
    setApplications(state, applications) {
      state.applications = applications
    },
    setApplicationSummary(state, summary) {
      state.applicationSummary = summary
    },
    addApplication(state, application) {
      state.applications.unshift(application)
    },
    updateApplication(state, updatedApplication) {
      const index = state.applications.findIndex(
        app => app.application_id === updatedApplication.application_id
      )
      if (index !== -1) {
        state.applications.splice(index, 1, updatedApplication)
      }
    },

    // INTERVIEWS
    setInterviews(state, interviews) {
      state.interviews = interviews
    },
    setInterviewSummary(state, summary) {
      state.interviewSummary = summary
    },
    addInterview(state, interview) {
      state.interviews.unshift(interview)
    },
    updateInterview(state, updatedInterview) {
      const index = state.interviews.findIndex(
        int => int.interview_id === updatedInterview.interview_id
      )
      if (index !== -1) {
        state.interviews.splice(index, 1, updatedInterview)
      }
    },
    removeInterview(state, interviewId) {
      state.interviews = state.interviews.filter(
        int => int.interview_id !== interviewId
      )
    },

    // STATUS
    setLoading(state, loading) {
      state.loading = loading
    },
    setError(state, error) {
      state.error = error
      state.loading = false
    },
    clearError(state) {
      state.error = null
    },

    // APPLICANT ID (after login)
    setApplicantId(state, id) {
      state.applicant_id = id
    },
  },

  // -------------------------------------------------------------
  // ACTIONS
  // -------------------------------------------------------------
  actions: {
    // Called after applicant login
    saveApplicantLogin({ commit }, loginData) {
      commit("setApplicantId", loginData.applicant_id)
    },

    // ------------------------------------------------------------------
    // PROFILE
    // ------------------------------------------------------------------
    async fetchProfile({ commit, rootState }) {
      commit("setLoading", true)
      try {
        const user = rootState.auth.currentUser
        if (!user || !user.id)
          throw new Error("Applicant ID not found")

        const res = await api.get(`/applicant_profile/${user.id}`)
        const data = res.data

        // guarantee arrays/objects exist
        data.skills = data.skills || []
        data.education = data.education || []
        data.work_experience = data.work_experience || []
        data.certifications = data.certifications || []
        data.personal_info = data.personal_info || {}
        data.resume = data.resume || {}

        commit("setProfile", data)
        commit("clearError")
      } catch (err) {
        commit("setError",
          err.response?.data?.message || "Failed to fetch profile"
        )
      } finally {
        commit("setLoading", false)
      }
    },

    async updateProfile({ commit, rootState }, payload) {
      commit("setLoading", true)
      try {
        const user = rootState.auth.currentUser
        if (!user || !user.id)
          throw new Error("Applicant ID not found")

        const res = await api.put(
          `/applicant/${user.id}`,
          payload,
          { headers: { "Content-Type": "multipart/form-data" } }
        )

        commit("setProfile", res.data)
        commit("clearError")
        return res.data
      } catch (err) {
        commit("setError",
          err.response?.data?.message || "Failed to update profile"
        )
        throw err
      } finally {
        commit("setLoading", false)
      }
    },

    // ------------------------------------------------------------------
    // APPLICATIONS
    // ------------------------------------------------------------------
    async fetchMyApplications({ commit, rootState }) {
      commit("setLoading", true)
      try {
        const user = rootState.auth.currentUser
        if (!user || !user.id)
          throw new Error("Applicant ID not found")

        const res = await api.get(`/applications/applicant/${user.id}`)

        commit("setApplications", res.data.applications || [])
        commit("setApplicationSummary", res.data.summary || {})
        commit("clearError")

        return res.data
      } catch (err) {
        commit("setError",
          err.response?.data?.message || "Failed to fetch applications"
        )
        throw err
      } finally {
        commit("setLoading", false)
      }
    },

    // OLD METHOD (kept)
    async applyForJob({ commit, rootState }, { jobId, applicationData }) {
      commit("setLoading", true)
      try {
        const user = rootState.auth.currentUser
        if (!user || !user.id)
          throw new Error("Applicant ID not found")

        const res = await api.post("/application", {
          job_id: jobId,
          applicant_id: user.id,
          ...applicationData,
        })

        commit("addApplication", res.data)
        commit("clearError")
        return res.data
      } catch (err) {
        commit("setError",
          err.response?.data?.message || "Failed to apply for job"
        )
        throw err
      } finally {
        commit("setLoading", false)
      }
    },

    // NEW CORRECT apply route
    async applyForJobCorrected({ rootState }, { jobId, resumeFilename }) {
      const user = rootState.auth.currentUser
      if (!user || !user.id)
        throw new Error("Applicant ID not found")

      const res = await api.post(`/applications/apply`, {
        applicant_id: user.id,
        job_id: jobId,
        resume_filename: resumeFilename,
      })

      return res.data
    },

    // ------------------------------------------------------------------
    // JOB OPPORTUNITIES
    // ------------------------------------------------------------------
    async fetchJobOpportunities({ rootState },
      { role = "", search = "", page = 1, perPage = 16 }
    ) {
      const user = rootState.auth.currentUser
      if (!user || !user.id)
        throw new Error("Applicant ID not found")

      const res = await api.get(
        `/job/opportunities/${user.id}`,
        {
          params: { role, search, page, per_page: perPage }
        }
      )

      return res.data
    },

    // ------------------------------------------------------------------
    // JOB DETAILS (NEW)
    // ------------------------------------------------------------------
    async fetchJobDetails({ state, rootState }, jobId) {
      const user = rootState.auth.currentUser
      const applicantId = user?.id || state.applicant_id

      if (!applicantId)
        throw new Error("Applicant ID not found")

      const res = await api.get(`/job/detail/${jobId}/${applicantId}`)
      return res.data
    },

    // ------------------------------------------------------------------
    // INTERVIEWS
    // ------------------------------------------------------------------
    async fetchMyInterviews({ commit, rootState }) {
      commit("setLoading", true)
      try {
        const user = rootState.auth.currentUser
        console.log('🔍 currentUser from auth store:', user)
        console.log('🔍 user.id:', user?.id)

        if (!user || !user.id)
          throw new Error("Applicant ID not found")

        const applicantId = user.id

        console.log('🔍 Making API call to:', `/interview/applicant/${applicantId}/list`)

        const list = await api.get(`/interview/applicant/${applicantId}/list`)
        const summary = await api.get(`/interview/applicant/${applicantId}/summary`)

        console.log('🔍 API response:', list.data)

        commit("setInterviews", list.data || [])
        commit("setInterviewSummary", summary.data || {})
        commit("clearError")
      } catch (err) {
        console.error('🔴 Error fetching interviews:', err)
        commit("setError",
          err.response?.data?.message || "Failed to fetch interviews"
        )
        throw err
      } finally {
        commit("setLoading", false)
      }
    },

    async cancelInterview({ commit }, interviewId) {
      try {
        await api.put(`/interview/${interviewId}/cancel`)
        commit("removeInterview", interviewId)
      } catch (err) {
        commit("setError",
          err.response?.data?.message || "Failed to cancel interview"
        )
        throw err
      }
    },
  },

  // -------------------------------------------------------------
  // GETTERS
  // -------------------------------------------------------------
  getters: {
    profile: s => s.profile,

    applications: s => s.applications,
    applicationSummary: s => s.applicationSummary,

    interviews: s => s.interviews,
    interviewSummary: s => s.interviewSummary,

    upcomingInterviews: s =>
      s.interviews.filter(int => {
        if (int.status !== "scheduled") return false
        return new Date(int.interview_date) >= new Date()
      }),

    loading: s => s.loading,
    error: s => s.error,

    // ID getter
    applicantId: s => s.applicant_id,
  },
}

export async function createApplication(applicantId, jobId) {
  try {
    const res = await api.post("/application", {
      applicant_id: applicantId,
      job_id: jobId,
    })
    const applicationId = res.data.id || res.data.application_id
    return {
      success: true,
      application_id: applicationId,
      data: res.data,
    }
  } catch (err) {
    return {
      success: false,
      error: err.response?.data?.message || err.message || "Failed to create application",
    }
  }
}

