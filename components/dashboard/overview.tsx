import { Suspense } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Package, DollarSign, AlertTriangle, TrendingUp } from 'lucide-react'
import { formatCurrency } from '@/lib/utils'
import { StatsCards } from './stats-cards'
import { RecentActivity } from './recent-activity'
import { LowStockAlerts } from './low-stock-alerts'

export function DashboardOverview() {
  return (
    <div className="space-y-6">
      <Suspense fallback={<div>Loading stats...</div>}>
        <StatsCards />
      </Suspense>
      
      <div className="grid gap-6 md:grid-cols-2">
        <Suspense fallback={<div>Loading activity...</div>}>
          <RecentActivity />
        </Suspense>
        
        <Suspense fallback={<div>Loading alerts...</div>}>
          <LowStockAlerts />
        </Suspense>
      </div>
    </div>
  )
}