import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const VALID_USERNAME = import.meta.env.VITE_LOGIN_USERNAME || ''
const VALID_PASSWORD = import.meta.env.VITE_LOGIN_PASSWORD || ''
const API_KEY = import.meta.env.VITE_API_KEY || ''

// Debug log for development
console.log('Login credentials loaded:', {
  hasUsername: !!VALID_USERNAME,
  hasPassword: !!VALID_PASSWORD,
  hasApiKey: !!API_KEY,
  username: VALID_USERNAME
})

export function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    console.log('Login attempt:', { username, usernameMatch: username === VALID_USERNAME, passwordMatch: password === VALID_PASSWORD })

    if (username === VALID_USERNAME && password === VALID_PASSWORD) {
      sessionStorage.setItem('authenticated', 'true')
      sessionStorage.setItem('apiKey', API_KEY)
      navigate('/')
    } else {
      setError('Invalid username or password')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="bg-white p-6 sm:p-8 rounded-xl shadow-2xl w-full max-w-md">
        <div className="text-center mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-2">PAGENT Untis</h1>
          <p className="text-sm sm:text-base text-gray-600">Parent Dashboard Login</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Enter your username"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Enter your password"
              required
            />
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors duration-200"
          >
            Sign In
          </button>
        </form>
      </div>
    </div>
  )
}
