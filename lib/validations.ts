import { z } from 'zod'

export const itemSchema = z.object({
  name: z.string().min(1, 'Name is required').max(255, 'Name too long'),
  description: z.string().optional(),
  sku: z.string().min(1, 'SKU is required').max(50, 'SKU too long'),
  barcode: z.string().optional(),
  price: z.number().min(0, 'Price must be positive'),
  cost: z.number().min(0, 'Cost must be positive').optional(),
  quantity: z.number().int().min(0, 'Quantity must be non-negative'),
  minStockLevel: z.number().int().min(0, 'Minimum stock level must be non-negative'),
  maxStockLevel: z.number().int().min(0, 'Maximum stock level must be non-negative').optional(),
  location: z.string().optional(),
  imageUrl: z.string().url('Invalid URL').optional().or(z.literal('')),
  categoryId: z.string().optional(),
  supplierId: z.string().optional(),
})

export const categorySchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name too long'),
  description: z.string().optional(),
  color: z.string().regex(/^#[0-9A-F]{6}$/i, 'Invalid color format'),
})

export const supplierSchema = z.object({
  name: z.string().min(1, 'Name is required').max(255, 'Name too long'),
  email: z.string().email('Invalid email').optional().or(z.literal('')),
  phone: z.string().optional(),
  address: z.string().optional(),
  contactPerson: z.string().optional(),
})

export const transactionSchema = z.object({
  type: z.enum(['IN', 'OUT', 'ADJUSTMENT']),
  quantity: z.number().int().min(1, 'Quantity must be positive'),
  reason: z.string().optional(),
  notes: z.string().optional(),
  itemId: z.string().min(1, 'Item is required'),
})

export type ItemFormData = z.infer<typeof itemSchema>
export type CategoryFormData = z.infer<typeof categorySchema>
export type SupplierFormData = z.infer<typeof supplierSchema>
export type TransactionFormData = z.infer<typeof transactionSchema>