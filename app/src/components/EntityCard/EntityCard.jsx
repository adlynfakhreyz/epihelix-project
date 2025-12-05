'use client'

import React from 'react'
import PropTypes from 'prop-types'
import { motion } from 'framer-motion'
import Link from 'next/link'
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
  }

  const variant = typeVariants[entity.type] || 'outline'

  return (
    <motion.div
      {...scaleIn}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      <Link href={`/entity/${entity.id}`}>
        <Card className="hover:border-cyan-500/50 hover:shadow-lg hover:shadow-cyan-500/10 group cursor-pointer">
          <CardContent className="p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <h3 className="font-semibold text-foreground group-hover:text-cyan-400 transition-colors duration-200 truncate">
                    {entity.label}
                  </h3>
                  <Badge variant={variant} className="whitespace-nowrap">
                    {entity.type}
                  </Badge>
                </div>

                {entity.snippet && (
                  <p className="text-sm text-muted-foreground line-clamp-2">{entity.snippet}</p>
                )}

                {entity.source && (
                  <div className="mt-2 text-xs text-muted-foreground">
                    Source: {entity.source}
                  </div>
                )}
              </div>
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
