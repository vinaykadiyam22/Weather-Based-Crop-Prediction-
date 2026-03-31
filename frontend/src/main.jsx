import React from 'react'
import ReactDOM from 'react-dom/client'
import axios from 'axios'
import './i18n'
import App from './App'
import './styles/index.css'

// Set global axios base URL for deployment
// In development, Vite proxy handles it
// In production, we'll use the environment variable
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
axios.defaults.baseURL = API_BASE_URL

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
)
