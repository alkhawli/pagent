import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { DashboardProvider } from './context/DashboardContext'
import { ChatPage } from './pages/ChatPage'
import { MessagesPage } from './pages/MessagesPage'
import { OverviewPage } from './pages/OverviewPage'

function App() {
  return (
    <DashboardProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<OverviewPage />} />
            <Route path="messages" element={<MessagesPage />} />
            <Route path="chat" element={<ChatPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </DashboardProvider>
  )
}

export default App
