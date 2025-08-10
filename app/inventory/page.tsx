import { Sidebar } from '@/components/layout/sidebar'
import { Header } from '@/components/layout/header'
import { InventoryTable } from '@/components/inventory/inventory-table'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'
import Link from 'next/link'

export default function InventoryPage() {
  return (
    <div className="flex h-screen">
      <div className="w-64 flex-shrink-0">
        <Sidebar />
      </div>
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-auto p-6">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Inventory</h1>
                <p className="text-gray-600">Manage your inventory items</p>
              </div>
              
              <Link href="/inventory/new">
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Item
                </Button>
              </Link>
            </div>
            
            <InventoryTable />
          </div>
        </main>
      </div>
    </div>
  )
}