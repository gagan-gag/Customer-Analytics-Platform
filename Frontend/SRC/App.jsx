import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { BarChart3, Users, TrendingUp, Target, AlertCircle, DollarSign, Settings } from 'lucide-react'
import DashboardPage from './pages/DashboardPage'
import CustomersPage from './pages/CustomersPage'
import SegmentationPage from './pages/SegmentationPage'
import ChurnAnalysisPage from './pages/ChurnAnalysisPage'
import CLVPage from './pages/CLVPage'
import RecommendationsPage from './pages/RecommendationsPage'

function App() {
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', path: '/', icon: BarChart3 },
    { name: 'Customers', path: '/customers', icon: Users },
    { name: 'Segmentation', path: '/segmentation', icon: Target },
    { name: 'Churn Analysis', path: '/churn', icon: AlertCircle },
    { name: 'Customer Value', path: '/clv', icon: DollarSign },
    { name: 'Recommendations', path: '/recommendations', icon: TrendingUp },
  ]

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <BarChart3 size={32} />
            <span>Analytics</span>
          </div>
        </div>
        
        <nav>
          <ul className="nav-menu">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              
              return (
                <li key={item.path} className="nav-item">
                  <Link 
                    to={item.path} 
                    className={`nav-link ${isActive ? 'active' : ''}`}
                  >
                    <Icon size={20} />
                    <span>{item.name}</span>
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/customers" element={<CustomersPage />} />
          <Route path="/segmentation" element={<SegmentationPage />} />
          <Route path="/churn" element={<ChurnAnalysisPage />} />
          <Route path="/clv" element={<CLVPage />} />
          <Route path="/recommendations" element={<RecommendationsPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
