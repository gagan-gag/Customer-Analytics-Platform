import { useQuery } from '@tanstack/react-query'
import { getRecommendations, getRetentionStrategies } from '../services/api'
import { Lightbulb, Target, AlertCircle } from 'lucide-react'

const PRIORITY_COLORS = {
  'Critical': '#ef4444',
  'High': '#f59e0b',
  'Medium': '#3b82f6',
  'Low': '#6b7280'
}

export default function RecommendationsPage() {
  const { data: strategies, isLoading: strategiesLoading } = useQuery({
    queryKey: ['retention-strategies'],
    queryFn: () => getRetentionStrategies().then(res => res.data)
  })

  const { data: recommendations, isLoading: recommendationsLoading } = useQuery({
    queryKey: ['recommendations'],
    queryFn: () => getRecommendations(null, 100).then(res => res.data)
  })

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Retention Strategies & Recommendations</h1>
        <p className="page-description">
          AI-powered actionable recommendations for customer retention
        </p>
      </div>

      {/* Retention Strategies */}
      <div className="mb-xl">
        <h2 className="mb-lg">Retention Strategies by Segment</h2>
        <div className="grid grid-2">
          {strategiesLoading ? (
            <div className="loading"><div className="spinner"></div></div>
          ) : (
            strategies?.map((strategy, index) => (
              <div 
                key={index} 
                className="card" 
                style={{ borderLeft: `4px solid ${PRIORITY_COLORS[strategy.priority] || '#3b82f6'}` }}
              >
                <div className="flex gap-md mb-md">
                  <Target size={24} style={{ color: PRIORITY_COLORS[strategy.priority] }} />
                  <div style={{ flex: 1 }}>
                    <h3 className="mb-sm">{strategy.segment}</h3>
                    <div className="flex gap-sm mb-sm">
                      <span className={`badge badge-${
                        strategy.priority === 'Critical' ? 'danger' :
                        strategy.priority === 'High' ? 'warning' :
                        strategy.priority === 'Medium' ? 'info' : 'secondary'
                      }`}>
                        {strategy.priority} Priority
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="mb-md">
                  <strong className="text-sm text-secondary">Strategy:</strong>
                  <p className="mt-sm">{strategy.strategy}</p>
                </div>

                <div className="mb-md">
                  <strong className="text-sm text-secondary">Recommended Actions:</strong>
                  <ul style={{ marginLeft: '1.5rem', marginTop: 'var(--spacing-sm)' }}>
                    {strategy.actions?.map((action, i) => (
                      <li key={i} className="text-sm mb-xs">{action}</li>
                    ))}
                  </ul>
                </div>

                <div className="text-sm" style={{ 
                  padding: 'var(--spacing-sm)', 
                  background: 'var(--bg-secondary)', 
                  borderRadius: 'var(--radius-sm)' 
                }}>
                  <strong>Expected Impact:</strong> {strategy.expected_impact}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Customer-Specific Recommendations */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Customer-Specific Recommendations</h3>
        </div>
        
        {recommendationsLoading ? (
          <div className="loading"><div className="spinner"></div></div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Customer</th>
                  <th>Segment</th>
                  <th>Churn Risk</th>
                  <th>CLV Segment</th>
                  <th>Priority</th>
                  <th>Recommended Actions</th>
                </tr>
              </thead>
              <tbody>
                {recommendations?.slice(0, 50).map((rec, index) => (
                  <tr key={index}>
                    <td>
                      <strong>{rec.customer_name}</strong>
                      <div className="text-sm text-secondary">ID: {rec.customer_id}</div>
                    </td>
                    <td>{rec.segment}</td>
                    <td>
                      <span className={`badge badge-${
                        rec.churn_risk === 'High' ? 'danger' :
                        rec.churn_risk === 'Medium' ? 'warning' : 'success'
                      }`}>
                        {rec.churn_risk}
                      </span>
                    </td>
                    <td>
                      <span className={`badge badge-${
                        rec.clv_segment?.includes('High') ? 'success' :
                        rec.clv_segment?.includes('Medium') ? 'info' : 'warning'
                      }`}>
                        {rec.clv_segment}
                      </span>
                    </td>
                    <td>
                      <span className={`badge badge-${
                        rec.priority === 'Critical' ? 'danger' :
                        rec.priority === 'High' ? 'warning' : 'info'
                      }`}>
                        {rec.priority}
                      </span>
                    </td>
                    <td>
                      <ul style={{ margin: 0, paddingLeft: '1.2rem' }}>
                        {rec.recommended_actions?.slice(0, 3).map((action, i) => (
                          <li key={i} className="text-sm">{action}</li>
                        ))}
                      </ul>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
