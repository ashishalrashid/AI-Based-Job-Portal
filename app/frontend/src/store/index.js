import { createStore } from 'vuex'
import auth from './modules/auth'
import hr from './modules/hr'
import applicant from './modules/applicant'
import organization from './modules/organization'
import ui from './modules/ui'
import theme from './modules/theme'

export default createStore({
  modules: {
    auth,
    hr,
    applicant,
    organization,
    ui,
    theme, // Add this
  },
})
