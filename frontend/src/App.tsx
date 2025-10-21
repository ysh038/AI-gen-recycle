import { Routes, Route, Navigate } from 'react-router-dom'

import { Home } from './routes'
import { Login, AuthCallback } from './routes'
import { useAuthStore } from './stores/shared/user'

function App() {
    const isAuthenticated = useAuthStore((state) => state.isAuthenticated())
    return (
        <Routes>
            <Route
                path="/"
                element={isAuthenticated ? <Home /> : <Navigate to="/login" />}
            />
            <Route path="/login" element={<Login />} />
            <Route path="/auth/callback" element={<AuthCallback />} />
        </Routes>
    )
}

export default App
