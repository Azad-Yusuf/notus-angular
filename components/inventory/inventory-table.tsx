import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { formatCurrency, formatDate } from '@/lib/utils'
import { prisma } from '@/lib/prisma'
import { Edit, Trash2, Eye, Search } from 'lucide-react'
import Link from 'next/link'

async function getInventoryItems() {
  return await prisma.item.findMany({
    include: {
      category: true,
      supplier: true,
    },
    where: {
      isActive: true
    },
    orderBy: {
      updatedAt: 'desc'
    }
  })
}

function getStockStatus(quantity: number, minStockLevel: number) {
  if (quantity === 0) {
    return { label: 'Out of Stock', color: 'bg-red-100 text-red-800' }
  } else if (quantity <= minStockLevel) {
    return { label: 'Low Stock', color: 'bg-yellow-100 text-yellow-800' }
  } else {
    return { label: 'In Stock', color: 'bg-green-100 text-green-800' }
  }
}

export async function InventoryTable() {
  const items = await getInventoryItems()

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>All Items ({items.length})</CardTitle>
          
          <div className="flex items-center space-x-2">
            <div className="relative">
              <Search className="absolute left-2 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <Input
                placeholder="Search items..."
                className="pl-8 w-64"
              />
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="rounded-md border">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="text-left p-4 font-medium">Item</th>
                  <th className="text-left p-4 font-medium">SKU</th>
                  <th className="text-left p-4 font-medium">Category</th>
                  <th className="text-left p-4 font-medium">Quantity</th>
                  <th className="text-left p-4 font-medium">Price</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-left p-4 font-medium">Updated</th>
                  <th className="text-left p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => {
                  const stockStatus = getStockStatus(item.quantity, item.minStockLevel)
                  
                  return (
                    <tr key={item.id} className="border-b hover:bg-gray-50">
                      <td className="p-4">
                        <div>
                          <div className="font-medium text-gray-900">{item.name}</div>
                          {item.description && (
                            <div className="text-sm text-gray-500 truncate max-w-xs">
                              {item.description}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="p-4">
                        <code className="text-sm bg-gray-100 px-2 py-1 rounded">
                          {item.sku}
                        </code>
                      </td>
                      <td className="p-4">
                        {item.category ? (
                          <Badge variant="outline" style={{ borderColor: item.category.color }}>
                            {item.category.name}
                          </Badge>
                        ) : (
                          <span className="text-gray-400">No category</span>
                        )}
                      </td>
                      <td className="p-4">
                        <div className="text-sm">
                          <div className="font-medium">{item.quantity}</div>
                          <div className="text-gray-500">Min: {item.minStockLevel}</div>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="text-sm">
                          <div className="font-medium">{formatCurrency(item.price)}</div>
                          {item.cost && (
                            <div className="text-gray-500">Cost: {formatCurrency(item.cost)}</div>
                          )}
                        </div>
                      </td>
                      <td className="p-4">
                        <Badge className={stockStatus.color}>
                          {stockStatus.label}
                        </Badge>
                      </td>
                      <td className="p-4 text-sm text-gray-500">
                        {formatDate(item.updatedAt)}
                      </td>
                      <td className="p-4">
                        <div className="flex items-center space-x-2">
                          <Link href={`/inventory/${item.id}`}>
                            <Button variant="ghost" size="sm">
                              <Eye className="h-4 w-4" />
                            </Button>
                          </Link>
                          <Link href={`/inventory/${item.id}/edit`}>
                            <Button variant="ghost" size="sm">
                              <Edit className="h-4 w-4" />
                            </Button>
                          </Link>
                          <Button variant="ghost" size="sm">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
          
          {items.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">No inventory items found</p>
              <p className="text-sm text-gray-400 mt-1">
                Get started by adding your first item
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}