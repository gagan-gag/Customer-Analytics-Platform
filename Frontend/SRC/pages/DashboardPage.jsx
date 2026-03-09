import { useQuery } from '@tanstack/react-query'
import { getDashboardMetrics, getStatsOverview, getRFMSegments } from '../services/api'
import { TrendingUp, Users, IndianRupee, ShoppingCart, AlertTriangle } from 'lucide-react'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: () => getStatsOverview().then(res => res.data)
  })

  const { data: dashboard, isLoading: dashboardLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => getDashboardMetrics().then(res => res.data)
  })

  const { data: segments, isLoading: segmentsLoading } = useQuery({
    queryKey: ['rfm-segments'],
    queryFn: () => getRFMSegments().then(res => res.data)
  })

  if (statsLoading || dashboardLoading) {
    return <div className="loading"><div className="spinner"></div></div>
  }

  const statCards = [
    {
      label: 'Total Customers',
      value: stats?.total_customers?.toLocaleString() || '0',
      icon: Users,
      color: 'primary'
    },
    {
      label: 'Total Revenue',
      value: `₹${stats?.total_revenue?.toLocaleString() || '0'}`,
      icon: IndianRupee,
      color: 'secondary'
    },
    {
      label: 'Avg Order Value',
      value: `₹${dashboard?.avg_order_value?.toFixed(2) || '0'}`,
      icon: ShoppingCart,
      color: 'accent'
    },
    {
      label: 'Churn Rate',
      value: `${(dashboard?.churn_rate * 100)?.toFixed(1) || '0'}%`,
      icon: AlertTriangle,
      color: 'warning'
    }
  ]

  // Prepare segment data for chart
  const segmentChartData = segments?.map(seg => ({
    name: seg.segment,
    customers: seg.customer_count,
    value: seg.total_value
  })) || []

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-description">
          Overview of customer analytics and key performance metrics
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-4 mb-xl">
        {statCards.map((stat, index) => {
          const Icon = stat.icon
          return (
            <div key={index} className={`stat-card ${stat.color}`}>
              <div className="flex-between">
                <div>
                  <div className="stat-label">{stat.label}</div>
                  <div className="stat-value">{stat.value}</div>
                </div>
                <Icon size={40} style={{ opacity: 0.8 }} />
              </div>
            </div>
          )
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-2">
        {/* Segment Distribution */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Customer Segments</h3>
          </div>
          <div className="card-body">
            {segmentsLoading ? (
              <div className="loading"><div className="spinner"></div></div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={segmentChartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="customers"
                  >
                    {segmentChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Segment Value */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Segment Value Distribution</h3>
          </div>
          <div className="card-body">
            {segmentsLoading ? (
              <div className="loading"><div className="spinner"></div></div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={segmentChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#2563eb" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* Key Metrics Table */}
      <div className="card mt-lg">
        <div className="card-header">
          <h3 className="card-title">Segment Overview</h3>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Segment</th>
                <th>Customers</th>
                <th>Avg Recency (days)</th>
                <th>Avg Frequency</th>
                <th>Avg Monetary</th>
                <th>Total Value</th>
                <th>Percentage</th>
              </tr>
            </thead>
            <tbody>
              {segments?.map((seg, index) => (
                <tr key={index}>
                  <td><strong>{seg.segment}</strong></td>
                  <td>{seg.customer_count}</td>
                  <td>{seg.avg_recency?.toFixed(1)}</td>
                  <td>{seg.avg_frequency?.toFixed(1)}</td>
                  <td>₹{seg.avg_monetary?.toFixed(2)}</td>
                  <td>₹{seg.total_value?.toFixed(2)}</td>
                  <td>{seg.percentage}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
