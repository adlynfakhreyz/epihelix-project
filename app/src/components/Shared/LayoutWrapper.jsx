'use client'

import { usePathname } from 'next/navigation'
import { Footer } from './Footer'

export function LayoutWrapper({ children }) {
  const pathname = usePathname()
  const isHomePage = pathname === '/'
  const isChatPage = pathname === '/chat'

  return (
    <>
      <div className="flex-1">
        {isHomePage ? (
          // Home page: keep the translucent container
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="bg-card/30 backdrop-blur-md rounded-2xl border border-border/30 p-6 sm:p-8 lg:p-12 min-h-[calc(100vh-16rem)]">
              {children}
            </div>
          </div>
        ) : (
          // Other pages: full-screen translucent container with internal padding
          <div className="h-full">
            <div className="bg-card/30 backdrop-blur-md border-y border-border/30 min-h-[calc(100vh-4rem)] p-6 sm:p-8 lg:p-12">
              {children}
            </div>
          </div>
        )}
      </div>
      {!isChatPage && <Footer />}
    </>
  )
}
