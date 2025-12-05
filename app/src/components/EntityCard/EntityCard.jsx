'use client'

import React from 'react'
import PropTypes from 'prop-types'
import { motion } from 'framer-motion'
import Link from 'next/link'
import Image from 'next/image'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { scaleIn } from '../../lib/animations'

/**
 * EntityCard - displays entity summary in search results or lists
 * @param {Object} props
 * @param {Object} props.entity - Entity data
 */
export default function EntityCard({ entity }) {
  if (!entity) return null

  const typeVariants = {
    Disease: 'destructive',
    Outbreak: 'default',
    Location: 'secondary',
    Organization: 'outline',
    Person: 'secondary',
    Country: 'secondary',
  }

  const variant = typeVariants[entity.type] || 'outline'

  // Get thumbnail image from enriched properties
  const getThumbnailUrl = () => {
    if (!entity.properties) return null

    // For diseases: thumbnailUrl from DBpedia
    if (entity.type === 'Disease' && entity.properties.thumbnailUrl) {
      return entity.properties.thumbnailUrl
    }

    // For countries: countryThumbnail from DBpedia
    if (entity.type === 'Country' && entity.properties.countryThumbnail) {
      return entity.properties.countryThumbnail
    }

    return null
  }

  const thumbnailUrl = getThumbnailUrl()

  return (
    <motion.div
      {...scaleIn}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      <Link href={`/entity/${entity.id}`}>
        <Card className="hover:border-cyan-500/50 hover:shadow-lg hover:shadow-cyan-500/10 group cursor-pointer">
          <CardContent className="p-4">
            <div className="flex items-start gap-4">
              {/* Thumbnail Image */}
              {thumbnailUrl && (
                <div className="flex-shrink-0">
                  <div className="relative w-20 h-20 rounded-lg overflow-hidden bg-muted border border-border/50">
                    <Image
                      src={thumbnailUrl}
                      alt={entity.label}
                      fill
                      className="object-cover"
                      sizes="80px"
                      unoptimized
                    />
                  </div>
                </div>
              )}

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <h3 className="font-semibold text-foreground group-hover:text-cyan-400 transition-colors duration-200 truncate">
                    {entity.label}
                  </h3>
                  <Badge variant={variant} className="whitespace-nowrap">
                    {entity.type}
                  </Badge>
                  {entity.properties?.enriched && (
                    <Badge variant="outline" className="whitespace-nowrap text-xs border-cyan-500/30 text-cyan-400">
                      Enriched
                    </Badge>
                  )}
                </div>

                {entity.snippet && (
                  <p className="text-sm text-muted-foreground line-clamp-2">{entity.snippet}</p>
                )}

                {/* Show enriched info snippet */}
                {entity.properties && (
                  <div className="mt-2 flex flex-wrap gap-2 text-xs text-muted-foreground">
                    {entity.type === 'Disease' && entity.properties.icd10 && (
                      <span className="px-2 py-0.5 bg-muted/50 rounded">ICD-10: {entity.properties.icd10}</span>
                    )}
                    {entity.type === 'Country' && entity.properties.population && (
                      <span className="px-2 py-0.5 bg-muted/50 rounded">
                        Pop: {(entity.properties.population / 1_000_000).toFixed(1)}M
                      </span>
                    )}
                    {entity.type === 'Country' && entity.properties.continent && (
                      <span className="px-2 py-0.5 bg-muted/50 rounded">{entity.properties.continent}</span>
                    )}
                  </div>
                )}

                {entity.source && (
                  <div className="mt-2 text-xs text-muted-foreground">
                    Source: {entity.source}
                  </div>
                )}
              </div>

              {/* Score */}
              {entity.score && (
                <div className="flex-shrink-0">
                  <div className="text-sm font-medium text-cyan-400">
                    {(entity.score * 100).toFixed(0)}%
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  )
}

EntityCard.propTypes = {
  entity: PropTypes.shape({
    id: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    type: PropTypes.string,
    snippet: PropTypes.string,
    source: PropTypes.string,
    score: PropTypes.number,
  }).isRequired,
}
