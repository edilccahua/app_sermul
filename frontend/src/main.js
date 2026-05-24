import '@sap-theming/theming-base-content/content/Base/baseLib/sap_horizon/css_variables.css'
import 'fundamental-styles/dist/icon.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useThemeStore } from './stores/theme'
import './assets/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

const themeStore = useThemeStore()
themeStore.init()

app.mount('#app')
