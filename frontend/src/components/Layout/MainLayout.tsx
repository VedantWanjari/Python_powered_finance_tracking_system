import { useState } from 'react'
import Header from './Header'
import Sidebar from './Sidebar'

interface MainLayoutProps {
  children: React.ReactNode
}

export default function MainLayout({ children }: MainLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex flex-1 flex-col lg:min-w-0">
        <Header onMenuToggle={() => setSidebarOpen((o) => !o)} />
        <main className="flex-1 p-4 sm:p-6">{children}</main>
      </div>
    </div>
  )
}
