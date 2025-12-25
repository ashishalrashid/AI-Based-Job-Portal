// src/store/modules/hr.js
import api from "@/services/api";

export default {
  namespaced: true,

  state: {
    // Dashboard / interview stats
    dashboard: {
      acceptanceRate: 0,
      pendingOnboardings: 0,
      pendingFeedback: 0,
      jobStats: [],
      interviewsScheduledMonth: 0,
      interviewsScheduledWeek: 0,
      interviewsCompleted: 0,
      interviewsPendingFeedback: 0,
    },
    // jobs / candidates
    candidateRoles: [],
    candidatesList: [],

    // candidate profile
    candidateProfile: null,
    experience: [],
    education: [],
    projects: [],
    certifications: [],

    // interviews (cards)
    interviewCards: [],
    interviewEvaluation: null,

    // ✅ NEW: Video interviews with AI scores (Kept these root-level ones)
    companyInterviews: [],
    interviewDetails: null,

    // shortlisted candidates
    shortlistStats: {
      acceptance_rate: 0,
      offers_sent: 0,
      pending_interviews: 0,
      total_shortlisted: 0
    },
    shortlistedCandidates: [],
  },

  mutations: {
    // existing dashboard
    SET_DASHBOARD_ACCEPTANCE(state, rate) {
      state.dashboard.acceptanceRate = rate;
    },
    SET_DASHBOARD_ONBOARDINGS(state, count) {
      state.dashboard.pendingOnboardings = count;
    },
    SET_DASHBOARD_FEEDBACK(state, count) {
      state.dashboard.pendingFeedback = count;
    },

    // job stats
    SET_JOB_STATS(state, stats) {
      state.dashboard.jobStats = stats;
    },

    // candidates
    SET_CANDIDATE_ROLES(state, roles) {
      state.candidateRoles = roles;
    },
    SET_CANDIDATES_LIST(state, list) {
      state.candidatesList = list;
    },

    // candidate profile + parts
    SET_CANDIDATE_PROFILE(state, profile) {
      state.candidateProfile = profile;
    },
    SET_EXPERIENCE(state, list) {
      state.experience = list;
    },
    SET_EDUCATION(state, list) {
      state.education = list;
    },
    SET_PROJECTS(state, list) {
      state.projects = list;
    },
    SET_CERTIFICATIONS(state, list) {
      state.certifications = list;
    },

    // interviews / stats
    SET_INTERVIEWS_SCHEDULED_MONTH(state, count) {
      state.dashboard.interviewsScheduledMonth = count;
    },
    SET_INTERVIEWS_SCHEDULED_WEEK(state, count) {
      state.dashboard.interviewsScheduledWeek = count;
    },
    SET_INTERVIEWS_COMPLETED(state, count) {
      state.dashboard.interviewsCompleted = count;
    },
    SET_INTERVIEWS_PENDING_FEEDBACK(state, count) {
      state.dashboard.interviewsPendingFeedback = count;
    },

    // ✅ NEW: Video interviews mutations
    SET_COMPANY_INTERVIEWS(state, interviews) {
      state.companyInterviews = interviews
    },
    SET_INTERVIEW_DETAILS(state, details) {
      state.interviewDetails = details
    },

    // interview cards (KEEP ONLY ONE)
    SET_INTERVIEW_CARDS(state, cards) {
      state.interviewCards = cards;
    },

    SET_INTERVIEW_EVALUATION(state, data) {
      state.interviewEvaluation = data
    },

    UPDATE_INTERVIEW_DECISION(state, { interview_id, decision }) {
      if (!state.interviewCards) return
      const item = state.interviewCards.find(i => i.interview_id === interview_id || i.id === interview_id)
      if (item) item.status = decision
    },

    SET_SHORTLIST_STATS(state, stats) {
      state.shortlistStats = stats
    },

    SET_SHORTLISTED_LIST(state, list) {
      state.shortlistedCandidates = list
    },
  },

  actions: {
    /* ---------------------------
       HR dashboard / existing actions
    ----------------------------*/

    async getOfferAcceptanceRate({ commit }, companyId) {
      const res = await api.get(`/offer/acceptance_rate/${companyId}`);
      commit("SET_DASHBOARD_ACCEPTANCE", res.data.acceptance_rate || 0);
      return res.data;
    },

    async getPendingOnboardings({ commit }, companyId) {
      const res = await api.get(`/onboarding/pending_count/${companyId}`);
      commit("SET_DASHBOARD_ONBOARDINGS", res.data.pending_onboarding_count || 0);
      return res.data;
    },

    async getPendingFeedbackCount({ commit }, companyId) {
      const res = await api.get(`/interview/pending_feedback_count/${companyId}`);
      commit("SET_DASHBOARD_FEEDBACK", res.data.pending_feedback_count || 0);
      return res.data;
    },

    async getJobStats({ commit }, companyId) {
      const res = await api.get(`/job/stats/${companyId}`);
      commit("SET_JOB_STATS", res.data || []);
      return res.data;
    },

    /* ---------------------------
       Interview stats / cards
    ----------------------------*/

    async getInterviewsScheduledThisMonth({ commit }, companyId) {
      const res = await api.get(`/interview/stats/scheduled_month/${companyId}`);
      const count = res.data?.scheduled_month_count ?? res.data?.count ?? res.data ?? 0;
      commit("SET_INTERVIEWS_SCHEDULED_MONTH", Number(count) || 0);
      return res.data;
    },

    async getInterviewsScheduledThisWeek({ commit }, companyId) {
      const res = await api.get(`/interview/stats/scheduled_week/${companyId}`);
      const count = res.data?.scheduled_week_count ?? res.data?.count ?? res.data ?? 0;
      commit("SET_INTERVIEWS_SCHEDULED_WEEK", Number(count) || 0);
      return res.data;
    },

    async getInterviewsCompletedCount({ commit }, companyId) {
      const res = await api.get(`/interview/stats/completed/${companyId}`);
      const count = res.data?.completed_count ?? res.data?.count ?? res.data ?? 0;
      commit("SET_INTERVIEWS_COMPLETED", Number(count) || 0);
      return res.data;
    },

    async getInterviewsPendingFeedback({ commit }, companyId) {
      const res = await api.get(`/interview/stats/pending_feedback/${companyId}`);
      const count = res.data?.pending_feedback_count ?? res.data?.count ?? res.data ?? 0;
      commit("SET_INTERVIEWS_PENDING_FEEDBACK", Number(count) || 0);
      return res.data;
    },

    // interview card list
    async fetchInterviewCards({ commit }, companyId) {
      const res = await api.get(`/interview/cards/${companyId}`);
      const cards = Array.isArray(res.data) ? res.data : res.data?.cards ?? [];
      commit("SET_INTERVIEW_CARDS", cards);
      return cards;
    },

    /* ---------------------------
       Interview evaluation & decision
    ----------------------------*/
    async fetchInterviewEvaluation({ commit }, interviewId) {
      const res = await api.get(`/interview/evaluation/${interviewId}`)
      commit("SET_INTERVIEW_EVALUATION", res.data)
      return res.data
    },

    async updateInterviewDecision({ commit }, { interviewId, decision }) {
      const res = await api.put(`/interview/decision/${interviewId}`, {
        decision: decision
      })
      commit("UPDATE_INTERVIEW_DECISION", {
        interview_id: interviewId,
        decision
      })
      return res.data
    },

    /* ---------------------------
       ✅ NEW: Video interviews with AI scores
    ----------------------------*/
    async fetchCompanyInterviews({ commit, rootGetters }) {
      const companyId = rootGetters['auth/currentUser']?.companyId || rootGetters['auth/currentUser']?.companyid
      const res = await api.get(`/api/hr/interviews/${companyId}`)
      commit('SET_COMPANY_INTERVIEWS', res.data)
      return res.data
    },

    async fetchInterviewDetails({ commit }, { sessionId }) {
      const response = await axios.get(`/video-interview/session/${sessionId}/data`)
      commit('SET_INTERVIEW_DETAILS', response.data)
      return response.data
    },

    /* ---------------------------
       Candidate review – list page
    ----------------------------*/
    async fetchCandidateRoles({ commit }, companyId) {
      const res = await api.get(`/applications/${companyId}/roles`);
      commit("SET_CANDIDATE_ROLES", res.data.roles || []);
      return res.data.roles || [];
    },

    async fetchCandidates({ commit }, { companyId, role, search, page, perPage }) {
      const url = `/applications/${companyId}/candidates`;
      const res = await api.get(url, {
        params: { role, search, page, per_page: perPage },
      });
      commit("SET_CANDIDATES_LIST", res.data);
      return res.data;
    },

    /* ---------------------------
       Candidate profile page
    ----------------------------*/
    async fetchCandidateProfile({ commit }, applicationId) {
      const res = await api.get(`/applicant/profile/${applicationId}`);
      commit("SET_CANDIDATE_PROFILE", res.data);
      return res.data;
    },

    async fetchApplicationAIResults({ commit }, applicationId) {
      try {
        const res = await api.get(`/resumeparser/application/${applicationId}/ai-results`);
        return res.data;
      } catch (err) {
        console.error("Failed to fetch AI results:", err);
        throw err;
      }
    },

    async fetchCandidateExperience({ commit }, applicantId) {
      const res = await api.get(`/applicant/${applicantId}/experiences`);
      commit("SET_EXPERIENCE", res.data);
      return res.data;
    },

    async fetchCandidateEducation({ commit }, applicantId) {
      const res = await api.get(`/applicant/${applicantId}/education`);
      commit("SET_EDUCATION", res.data);
      return res.data;
    },

    async fetchCandidateProjects({ commit }, applicantId) {
      const res = await api.get(`/applicant/${applicantId}/projects`);
      commit("SET_PROJECTS", res.data);
      return res.data;
    },

    async fetchCandidateCertifications({ commit }, applicantId) {
      const res = await api.get(`/applicant/${applicantId}/certifications`);
      commit("SET_CERTIFICATIONS", res.data);
      return res.data;
    },

    /* ---------------------------
       ✅ UPDATED: Schedule / reject interview (CRITICAL)
    ----------------------------*/
    // ✅ REPLACED: Enhanced scheduleInterview with conflict handling
    scheduleInterview: async ({ commit }, { applicationId, hrId, form }) => {
      try {
        const response = await api.post(
          `/api/interview/schedule/${applicationId}/${hrId}`,
          {
            interview_date: form.interview_date,
            interview_time: form.interview_time,
            duration: form.duration || 60,
            stage: form.stage || 'Technical Round',
            mode: form.mode || 'online'
          }
        );

        return {
          success: true,
          interview: response.data.interview
        };

      } catch (error) {
        // ✅ Handle different error types for frontend
        if (error.response?.status === 409) {
          // Conflict: Interview already scheduled
          const data = error.response.data;
          throw {
            type: 'CONFLICT',
            status: 409,
            message: data.message,
            existingInterview: data.existing_interview
          };
        } else if (error.response?.status === 400) {
          // Bad request
          throw {
            type: 'BAD_REQUEST',
            status: 400,
            message: error.response.data.message
          };
        } else if (error.response?.status === 404) {
          // Not found
          throw {
            type: 'NOT_FOUND',
            status: 404,
            message: error.response.data.message
          };
        } else {
          // Other errors
          throw {
            type: 'ERROR',
            status: error.response?.status || 500,
            message: error.response?.data?.message || 'Failed to schedule interview'
          };
        }
      }
    },

    async rejectInterview(_, applicationId) {
      const res = await api.post(`/interview/reject/${applicationId}`);
      return res.data;
    },

    // ✅ UPDATED: Better fetchInterviewByApplication
    async fetchInterviewByApplication(_, applicationId) {
      try {
        const res = await api.get(`/api/interview/by-application/${applicationId}`);
        return res.data; // Returns array of interviews
      } catch (error) {
        console.error('Failed to fetch interviews:', error);
        return []; // Return empty array on error
      }
    },

    /* ---------------------------
       Create job
    ----------------------------*/
    async createJob(_, formData) {
      const res = await api.post("/job", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return res.data;
    },

    /* ============================================================
       SHORTLISTED CANDIDATES
    ============================================================ */
    async fetchShortlistStats({ commit }, companyId) {
      const res = await api.get(`/shortlist/${companyId}/stats`)
      commit("SET_SHORTLIST_STATS", res.data)
      return res.data
    },

    async fetchShortlistedCandidates({ commit }, { companyId, params }) {
      const res = await api.get(`/shortlist/${companyId}/candidates`, {
        params: {
          status: params.status || "",
          role: params.role || "",
          search: params.search || ""
        }
      })
      commit("SET_SHORTLISTED_LIST", res.data)
      return res.data
    },

    async rejectShortlisted(_, { applicationId }) {
      const res = await api.put(`/shortlist/reject/${applicationId}`)
      return res.data
    }
  },

  getters: {
    dashboard: (state) => state.dashboard,
    jobStats: (state) => state.dashboard.jobStats,

    roles: (state) => state.candidateRoles,
    candidates: (state) => state.candidatesList,

    candidateProfile: (state) => state.candidateProfile,
    experience: (state) => state.experience,
    education: (state) => state.education,
    projects: (state) => state.projects,
    certifications: (state) => state.certifications,

    interviewCards: (state) => state.interviewCards,
    interviewsScheduledMonth: (state) => state.dashboard.interviewsScheduledMonth,
    interviewsScheduledWeek: (state) => state.dashboard.interviewsScheduledWeek,
    interviewsCompleted: (state) => state.dashboard.interviewsCompleted,
    interviewsPendingFeedback: (state) => state.dashboard.interviewsPendingFeedback,
    interviewEvaluation: (state) => state.interviewEvaluation,

    // ✅ NEW getters
    companyInterviews: (state) => state.companyInterviews,
    interviewDetails: (state) => state.interviewDetails,

    shortlistStats: (state) => state.shortlistStats,
    shortlistedCandidates: (state) => state.shortlistedCandidates,
  },
};

