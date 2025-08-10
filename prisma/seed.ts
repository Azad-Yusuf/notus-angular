import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  console.log('🌱 Seeding database...')

  // Create categories
  const electronics = await prisma.category.create({
    data: {
      name: 'Electronics',
      description: 'Electronic devices and components',
      color: '#3B82F6',
    },
  })

  const office = await prisma.category.create({
    data: {
      name: 'Office Supplies',
      description: 'General office supplies and equipment',
      color: '#10B981',
    },
  })

  const furniture = await prisma.category.create({
    data: {
      name: 'Furniture',
      description: 'Office and home furniture',
      color: '#F59E0B',
    },
  })

  // Create suppliers
  const techSupplier = await prisma.supplier.create({
    data: {
      name: 'TechCorp Solutions',
      email: 'orders@techcorp.com',
      phone: '+1-555-0123',
      address: '123 Tech Street, Silicon Valley, CA 94000',
      contactPerson: 'John Smith',
    },
  })

  const officeSupplier = await prisma.supplier.create({
    data: {
      name: 'Office Depot Pro',
      email: 'business@officedepot.com',
      phone: '+1-555-0456',
      address: '456 Business Ave, Corporate City, NY 10001',
      contactPerson: 'Sarah Johnson',
    },
  })

  // Create items
  const items = [
    {
      name: 'Laptop - Dell XPS 13',
      description: 'High-performance ultrabook with 13-inch display',
      sku: 'DELL-XPS13-001',
      barcode: '1234567890123',
      price: 1299.99,
      cost: 899.99,
      quantity: 25,
      minStockLevel: 5,
      maxStockLevel: 50,
      location: 'Warehouse A-1',
      categoryId: electronics.id,
      supplierId: techSupplier.id,
    },
    {
      name: 'Wireless Mouse',
      description: 'Ergonomic wireless mouse with USB receiver',
      sku: 'MOUSE-WL-001',
      barcode: '1234567890124',
      price: 29.99,
      cost: 15.99,
      quantity: 120,
      minStockLevel: 20,
      maxStockLevel: 200,
      location: 'Warehouse A-2',
      categoryId: electronics.id,
      supplierId: techSupplier.id,
    },
    {
      name: 'Office Chair - Ergonomic',
      description: 'Adjustable ergonomic office chair with lumbar support',
      sku: 'CHAIR-ERG-001',
      barcode: '1234567890125',
      price: 199.99,
      cost: 129.99,
      quantity: 15,
      minStockLevel: 3,
      maxStockLevel: 30,
      location: 'Warehouse B-1',
      categoryId: furniture.id,
      supplierId: officeSupplier.id,
    },
    {
      name: 'A4 Paper Pack',
      description: 'High-quality A4 printer paper, 500 sheets',
      sku: 'PAPER-A4-001',
      barcode: '1234567890126',
      price: 8.99,
      cost: 4.99,
      quantity: 200,
      minStockLevel: 50,
      maxStockLevel: 500,
      location: 'Warehouse C-1',
      categoryId: office.id,
      supplierId: officeSupplier.id,
    },
    {
      name: 'Standing Desk',
      description: 'Height-adjustable standing desk with electric motor',
      sku: 'DESK-STAND-001',
      barcode: '1234567890127',
      price: 499.99,
      cost: 299.99,
      quantity: 8,
      minStockLevel: 2,
      maxStockLevel: 20,
      location: 'Warehouse B-2',
      categoryId: furniture.id,
      supplierId: officeSupplier.id,
    },
    {
      name: 'USB-C Hub',
      description: 'Multi-port USB-C hub with HDMI, USB 3.0, and charging',
      sku: 'HUB-USBC-001',
      barcode: '1234567890128',
      price: 79.99,
      cost: 45.99,
      quantity: 45,
      minStockLevel: 10,
      maxStockLevel: 100,
      location: 'Warehouse A-3',
      categoryId: electronics.id,
      supplierId: techSupplier.id,
    },
    {
      name: 'Ballpoint Pens (Pack of 10)',
      description: 'Black ink ballpoint pens, pack of 10',
      sku: 'PEN-BP-001',
      barcode: '1234567890129',
      price: 12.99,
      cost: 6.99,
      quantity: 3,
      minStockLevel: 15,
      maxStockLevel: 100,
      location: 'Warehouse C-2',
      categoryId: office.id,
      supplierId: officeSupplier.id,
    },
  ]

  for (const item of items) {
    await prisma.item.create({ data: item })
  }

  // Create some sample transactions
  const laptopItem = await prisma.item.findUnique({
    where: { sku: 'DELL-XPS13-001' },
  })

  const penItem = await prisma.item.findUnique({
    where: { sku: 'PEN-BP-001' },
  })

  if (laptopItem) {
    await prisma.transaction.create({
      data: {
        type: 'IN',
        quantity: 10,
        reason: 'Stock replenishment',
        notes: 'Monthly stock order from supplier',
        itemId: laptopItem.id,
      },
    })
  }

  if (penItem) {
    await prisma.transaction.create({
      data: {
        type: 'OUT',
        quantity: 12,
        reason: 'Office distribution',
        notes: 'Distributed to various departments',
        itemId: penItem.id,
      },
    })
  }

  console.log('✅ Seeding completed successfully!')
}

main()
  .catch((e) => {
    console.error('❌ Seeding failed:', e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })