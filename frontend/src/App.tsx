import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { DashboardProvider } from './context/DashboardContext'
import { ChatPage } from './pages/ChatPage'
import { LoginPage } from './pages/LoginPage'
import { MealPlanPage } from './pages/MealPlanPage'
import { MessagesPage } from './pages/MessagesPage'
import { NewsPage } from './pages/NewsPage'
import { OverviewPage } from './pages/OverviewPage'
import { TrendsPage } from './pages/TrendsPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          element={
            <ProtectedRoute>
              <DashboardProvider>
                <Layout />
              </DashboardProvider>
            </ProtectedRoute>
          }
        >
          <Route index element={<OverviewPage />} />
          <Route path="messages" element={<MessagesPage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="meal-plan" element={<MealPlanPage />} />
          <Route path="news" element={<NewsPage />} />
          <Route path="trends" element={<TrendsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
