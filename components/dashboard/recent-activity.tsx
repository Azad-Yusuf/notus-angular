import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { formatDate } from '@/lib/utils'
import { prisma } from '@/lib/prisma'
import { ArrowUpRight, ArrowDownRight, RotateCw } from 'lucide-react'

async function getRecentTransactions() {
  return await prisma.transaction.findMany({
    include: {
      item: true
    },
    orderBy: {
      createdAt: 'desc'
    },
    take: 5
  })
}

export async function RecentActivity() {
  const transactions = await getRecentTransactions()

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case 'IN':
        return <ArrowUpRight className="h-4 w-4 text-green-500" />
      case 'OUT':
        return <ArrowDownRight className="h-4 w-4 text-red-500" />
      case 'ADJUSTMENT':
        return <RotateCw className="h-4 w-4 text-blue-500" />
      default:
        return null
    }
  }

  const getTransactionColor = (type: string) => {
    switch (type) {
      case 'IN':
        return 'text-green-600'
      case 'OUT':
        return 'text-red-600'
      case 'ADJUSTMENT':
        return 'text-blue-600'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
        <CardDescription>Latest inventory transactions</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {transactions.map((transaction) => (
            <div key={transaction.id} className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                {getTransactionIcon(transaction.type)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {transaction.item.name}
                </p>
                <p className="text-sm text-gray-500">
                  {transaction.reason || 'No reason provided'}
                </p>
              </div>
              <div className="text-right">
                <p className={`text-sm font-medium ${getTransactionColor(transaction.type)}`}>
                  {transaction.type === 'IN' ? '+' : transaction.type === 'OUT' ? '-' : '±'}
                  {transaction.quantity}
                </p>
                <p className="text-xs text-gray-500">
                  {formatDate(transaction.createdAt)}
                </p>
              </div>
            </div>
          ))}
          {transactions.length === 0 && (
            <p className="text-sm text-gray-500 text-center py-4">
              No recent transactions
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}