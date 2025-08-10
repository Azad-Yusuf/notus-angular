import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Package, DollarSign, AlertTriangle, TrendingUp } from 'lucide-react'
import { formatCurrency } from '@/lib/utils'
import { prisma } from '@/lib/prisma'

async function getInventoryStats() {
  const [
    totalItems,
    totalValue,
    lowStockItems,
    totalTransactions
  ] = await Promise.all([
    prisma.item.count({ where: { isActive: true } }),
    prisma.item.aggregate({
      where: { isActive: true },
      _sum: { price: true }
    }),
    prisma.$queryRaw<[{ count: number }]>`
      SELECT COUNT(*) as count 
      FROM Item 
      WHERE isActive = 1 AND quantity <= minStockLevel
    `,
    prisma.transaction.count()
  ])

  return {
    totalItems,
    totalValue: totalValue._sum.price || 0,
    lowStockItems: lowStockItems[0].count,
    totalTransactions
  }
}

export async function StatsCards() {
  const stats = await getInventoryStats()

  const cards = [
    {
      title: 'Total Items',
      value: stats.totalItems.toString(),
      description: 'Active inventory items',
      icon: Package,
      color: 'text-blue-600'
    },
    {
      title: 'Total Value',
      value: formatCurrency(stats.totalValue),
      description: 'Current inventory value',
      icon: DollarSign,
      color: 'text-green-600'
    },
    {
      title: 'Low Stock Items',
      value: stats.lowStockItems.toString(),
      description: 'Items below minimum level',
      icon: AlertTriangle,
      color: 'text-red-600'
    },
    {
      title: 'Total Transactions',
      value: stats.totalTransactions.toString(),
      description: 'All-time transactions',
      icon: TrendingUp,
      color: 'text-purple-600'
    }
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card, index) => (
        <Card key={index}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {card.title}
            </CardTitle>
            <card.icon className={`h-4 w-4 ${card.color}`} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{card.value}</div>
            <p className="text-xs text-muted-foreground">
              {card.description}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}