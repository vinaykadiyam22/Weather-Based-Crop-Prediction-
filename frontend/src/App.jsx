import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import i18n from './i18n'
import Landing from './pages/Landing'
import About from './pages/About'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import SoilAnalysis from './pages/SoilAnalysis'
import CropRecommendation from './pages/CropRecommendation'
import Weather from './pages/Weather'
import DiseaseDetection from './pages/DiseaseDetection'
import SoilTypeDetection from './pages/SoilTypeDetection'
import MarketPrices from './pages/MarketPrices'
import AlertDetail from './pages/AlertDetail'
import AlertBanner from './components/AlertBanner'

function App() {
    const [user, setUser] = useState(null)

    // Load user from localStorage on mount, sync i18n language
    useEffect(() => {
        const savedUser = localStorage.getItem('user')
        if (savedUser) {
            const u = JSON.parse(savedUser)
            setUser(u)
            if (u?.language) i18n.changeLanguage(u.language)
        } else {
            i18n.changeLanguage(i18n.options.lng || 'en')
        }
    }, [])

    const handleLogin = (userData) => {
        setUser(userData)
        localStorage.setItem('user', JSON.stringify(userData))
        const lang = userData?.language || 'en'
        i18n.changeLanguage(lang)
    }

    const handleLogout = () => {
        setUser(null)
        localStorage.removeItem('user')
    }

    return (
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
            {/* Global Alert Banner - shows on all authenticated pages */}
            {user && <AlertBanner user={user} />}

            <Routes>
                <Route path="/" element={<Landing />} />
                <Route path="/about" element={<About />} />
                <Route path="/login" element={<Login onLogin={handleLogin} />} />
                <Route path="/register" element={<Register />} />

                {/* Protected routes */}
                <Route
                    path="/dashboard"
                    element={user ? <Dashboard user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/soil-analysis"
                    element={user ? <SoilAnalysis user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/crop-recommendation"
                    element={user ? <CropRecommendation user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/weather"
                    element={user ? <Weather user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/disease-detection"
                    element={user ? <DiseaseDetection user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/soil-detection"
                    element={user ? <SoilTypeDetection user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/market-prices"
                    element={user ? <MarketPrices user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route path="/alert/:id" element={user ? <AlertDetail user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />} />
            </Routes>
        </Router>
    )
}

export default App
