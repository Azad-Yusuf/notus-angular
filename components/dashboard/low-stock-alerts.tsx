import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { AlertTriangle } from 'lucide-react'
import { prisma } from '@/lib/prisma'

async function getLowStockItems() {
  return await prisma.$queryRaw<Array<{
    id: string
    name: string
    sku: string
    quantity: number
    minStockLevel: number
  }>>`
    SELECT id, name, sku, quantity, minStockLevel
    FROM Item
    WHERE isActive = 1 AND quantity <= minStockLevel
    ORDER BY (quantity - minStockLevel) ASC
    LIMIT 5
  `
}

export async function LowStockAlerts() {
  const lowStockItems = await getLowStockItems()

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <AlertTriangle className="h-5 w-5 text-red-500" />
          <span>Low Stock Alerts</span>
        </CardTitle>
        <CardDescription>Items that need immediate attention</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {lowStockItems.map((item) => (
            <div key={item.id} className="flex items-center justify-between space-x-3">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {item.name}
                </p>
                <p className="text-xs text-gray-500">
                  SKU: {item.sku}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-red-600 font-medium">
                  {item.quantity} / {item.minStockLevel}
                </p>
                <p className="text-xs text-gray-500">
                  Current / Min
                </p>
              </div>
            </div>
          ))}
          {lowStockItems.length === 0 && (
            <div className="text-center py-4">
              <p className="text-sm text-gray-500">No low stock items</p>
              <p className="text-xs text-gray-400">All items are well stocked!</p>
            </div>
          )}
          {lowStockItems.length > 0 && (
            <div className="pt-4">
              <Button variant="outline" className="w-full" size="sm">
                View All Low Stock Items
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}