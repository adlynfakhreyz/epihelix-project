'use client'

import React from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import InfoBox from '../../../components/InfoBox/InfoBox'
import useEntity from '../../../hooks/useEntity'

export default function EntityPage() {
  const params = useParams()
  const { entity, loading, error } = useEntity(params.id)

  return (
    <main className="flex-1 py-8 md:py-12">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl">
        {/* Breadcrumb */}
        <nav className="mb-4 md:mb-6 text-xs sm:text-sm">
          <Link href="/" className="text-cyan-400 hover:text-cyan-300 transition-colors">
            Home
          </Link>
          <span className="text-muted-foreground mx-2">/</span>
          <Link href="/search" className="text-cyan-400 hover:text-cyan-300 transition-colors">
            Search
          </Link>
          <span className="text-muted-foreground mx-2">/</span>
          <span className="text-muted-foreground">Entity</span>
        </nav>

        {/* Error State */}
        {error && (
          <div className="p-4 md:p-6 bg-destructive/10 border border-destructive/20 rounded-lg text-center">
            <p className="text-sm sm:text-base text-destructive-foreground">Error loading entity: {error}</p>
          </div>
        )}

        {/* Entity Info */}
        <InfoBox entity={entity} loading={loading} />

        {/* Actions */}
        {entity && (
          <div className="mt-6 flex gap-4">
            <Link
              href={`/graph/${entity.id}`}
              className="px-4 py-2 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 rounded-lg hover:bg-cyan-500/20 transition-colors"
            >
              View Graph
            </Link>
            <button className="px-4 py-2 bg-gray-800 text-gray-300 border border-gray-700 rounded-lg hover:bg-gray-700 transition-colors">
              Export Data
            </button>
          </div>
        )}
      </div>
    </main>
  )
}
