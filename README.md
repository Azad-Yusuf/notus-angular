# Modern Inventory Management System

A comprehensive, modern inventory management application built with the latest web technologies including Next.js 15, TypeScript, Prisma, and Tailwind CSS.

## ✨ Features

- **Dashboard Overview**: Real-time inventory statistics and insights
- **Inventory Management**: Complete CRUD operations for inventory items
- **Category & Supplier Management**: Organize items by categories and suppliers
- **Low Stock Alerts**: Automatic notifications for items below minimum stock levels
- **Transaction Tracking**: Complete audit trail of all inventory movements
- **Search & Filtering**: Advanced search capabilities across all inventory
- **Responsive Design**: Beautiful, modern UI that works on all devices
- **Real-time Updates**: Live data updates throughout the application

## 🚀 Tech Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Radix UI** - Accessible component primitives
- **Lucide React** - Beautiful icons
- **React Hook Form** - Performant forms with validation

### Backend
- **Prisma ORM** - Type-safe database operations
- **SQLite** - Lightweight, serverless database
- **Zod** - Schema validation

### Development Tools
- **ESLint** - Code linting
- **PostCSS** - CSS processing
- **tsx** - TypeScript execution

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd modern-inventory-app
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up the database**
   ```bash
   npx prisma generate
   npx prisma db push
   npm run db:seed
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🗄️ Database Schema

The application uses a comprehensive database schema with the following entities:

- **Items**: Core inventory items with SKU, pricing, stock levels
- **Categories**: Organization by product categories
- **Suppliers**: Vendor and supplier information
- **Transactions**: Complete audit trail of inventory movements

## 🎯 Key Functionality

### Dashboard
- Total items count and value
- Low stock alerts
- Recent transaction activity
- Quick overview of inventory health

### Inventory Management
- Add, edit, view, and delete inventory items
- SKU generation and barcode support
- Image upload capability
- Stock level management with minimum/maximum thresholds

### Category Management
- Color-coded categories
- Hierarchical organization
- Easy filtering by category

### Supplier Management
- Complete supplier contact information
- Track items by supplier
- Supplier performance metrics

### Transaction System
- IN, OUT, and ADJUSTMENT transaction types
- Detailed reason and notes
- Automatic stock level updates
- Complete audit trail

## 🛠️ Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run db:push` - Push database schema
- `npm run db:generate` - Generate Prisma client
- `npm run db:seed` - Seed database with sample data

## 📱 Responsive Design

The application is fully responsive and provides an excellent user experience on:
- Desktop computers
- Tablets
- Mobile phones

## 🔒 Type Safety

Built with TypeScript throughout:
- Full type safety for database operations
- Validated forms with Zod schemas
- Type-safe API routes
- IntelliSense support

## 🎨 UI Components

Modern, accessible UI components built with:
- Radix UI primitives for accessibility
- Tailwind CSS for styling
- Custom design system with consistent theming
- Dark mode ready (can be enabled)

## 📊 Future Enhancements

Potential features for future releases:
- User authentication and roles
- Advanced reporting and analytics
- Barcode scanning
- Export/import functionality
- Multi-warehouse support
- Integration with e-commerce platforms
- Mobile app companion

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Next.js](https://nextjs.org/)
- UI components inspired by [shadcn/ui](https://ui.shadcn.com/)
- Icons by [Lucide](https://lucide.dev/)
- Database ORM by [Prisma](https://prisma.io/)

---

**Made with ❤️ using the latest web technologies**
