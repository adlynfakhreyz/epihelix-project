'use client'

import React from 'react'
import { use } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import InfoBox from '../../../components/InfoBox/InfoBox'
import { useEntity } from '../../../hooks/useEntity'

export default function EntityPage() {
  const params = useParams()
  const router = useRouter()
  const entityId = params.id
  
  const { data: entity, isLoading: loading, error } = useEntity(entityId)

  return (
    <main className="flex-1 py-8 md:py-12">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl">
        {/* Back Button */}
        <div className="mb-4 md:mb-6">
          <Button
            variant="ghost"
            onClick={() => router.back()}
            className="text-muted-foreground hover:text-foreground -ml-2"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
        </div>

        {/* Breadcrumb */}
        <nav className="mb-4 md:mb-6 text-xs sm:text-sm">
          <Link href="/" className="text-cyan-400 hover:text-cyan-300 transition-colors">
            Home
          </Link>
          <span className="text-muted-foreground mx-2">/</span>
          <Link href="/entities" className="text-cyan-400 hover:text-cyan-300 transition-colors">
            Entities
          </Link>
          <span className="text-muted-foreground mx-2">/</span>
          <span className="text-muted-foreground">{entity?.label || 'Loading...'}</span>
        </nav>

        {/* Error State */}
        {error && (
          <div className="p-4 md:p-6 bg-destructive/10 border border-destructive/20 rounded-lg text-center">
            <p className="text-sm sm:text-base text-destructive-foreground">
              Error loading entity: {error?.message || String(error)}
            </p>
          </div>
        )}

        {/* Entity Info */}
        <InfoBox entity={entity} loading={loading} />
      </div>
    </main>
  )
}
