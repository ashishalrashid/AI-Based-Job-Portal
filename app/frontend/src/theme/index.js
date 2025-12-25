import light from './light'
import dark from './dark'

const themes = { light, dark }

function applyTheme(theme) {
  Object.keys(theme.colors).forEach((key) => {
    document.documentElement.style.setProperty(`--${key}`, theme.colors[key])
  })
}

export default {
  themes,
  applyTheme,
}
