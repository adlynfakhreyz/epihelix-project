'use client'

import React from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Database,
  Globe,
  AlertCircle,
  Syringe,
  Building2,
  Network,
  ArrowRight,
} from 'lucide-react'
import { fadeIn } from '@/lib/animations'

const entityTypes = [
  {
    type: 'Country',
    icon: Globe,
    color: 'from-blue-500 to-cyan-500',
    description: 'Browse countries with demographic and geographic data enriched from Wikidata and DBpedia',
    count: '195+',
    examples: ['United States', 'India', 'Germany', 'Brazil'],
  },
  {
    type: 'Disease',
    icon: AlertCircle,
    color: 'from-red-500 to-orange-500',
    description: 'Explore infectious diseases with medical classifications, symptoms, and treatment data',
    count: '25+',
    examples: ['COVID-19', 'Measles', 'Tuberculosis', 'Cholera'],
  },
  {
    type: 'Outbreak',
    icon: Network,
    color: 'from-purple-500 to-pink-500',
    description: 'View historical outbreak records with case and death statistics across time and regions',
    count: '10,000+',
    examples: ['COVID-19 USA 2020', 'Cholera Haiti 2010', 'Measles UK 2019'],
  },
  {
    type: 'VaccinationRecord',
    icon: Syringe,
    color: 'from-green-500 to-emerald-500',
    description: 'Track vaccination coverage rates for preventable diseases across countries and years',
    count: '5,000+',
    examples: ['Measles Vaccination USA 2020', 'Polio Vaccination India 2015'],
  },
]

export default function EntitiesPage() {
  return (
    <main className="flex-1 py-8 md:py-12">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        {/* Header */}
        <motion.div {...fadeIn} className="mb-8 md:mb-12 text-center">
          <div className="inline-flex items-center justify-center p-2 bg-cyan-500/10 rounded-full mb-4">
            <Database className="h-6 w-6 text-cyan-400" />
          </div>
          <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            Entity Browser
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Explore the knowledge graph by entity type. Browse, search, and filter through thousands of entities.
          </p>
        </motion.div>

        {/* Entity Type Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {entityTypes.map((entity, index) => {
            const Icon = entity.icon
            return (
              <motion.div
                key={entity.type}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <Link href={`/entities/${entity.type.toLowerCase()}`}>
                  <Card className="h-full hover:border-cyan-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/10 group cursor-pointer">
                    <CardHeader>
                      <div className="flex items-start justify-between mb-4">
                        <div
                          className={`p-3 rounded-lg bg-gradient-to-br ${entity.color} bg-opacity-10`}
                        >
                          <Icon className="h-6 w-6 text-white" />
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {entity.count}
                        </Badge>
                      </div>
                      <CardTitle className="flex items-center justify-between">
                        <span className="group-hover:text-cyan-400 transition-colors">
                          {entity.type}
                        </span>
                        <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-cyan-400 group-hover:translate-x-1 transition-all" />
                      </CardTitle>
                      <CardDescription className="text-sm">
                        {entity.description}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <p className="text-xs text-muted-foreground font-medium">
                          Examples:
                        </p>
                        <div className="flex flex-wrap gap-1.5">
                          {entity.examples.slice(0, 3).map((example, idx) => (
                            <Badge
                              key={idx}
                              variant="secondary"
                              className="text-xs"
                            >
                              {example}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              </motion.div>
            )
          })}
        </div>

        {/* Stats Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="mt-12 p-6 bg-muted/30 rounded-lg border border-border/50"
        >
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-cyan-400">15,000+</p>
              <p className="text-sm text-muted-foreground">Total Entities</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-cyan-400">50,000+</p>
              <p className="text-sm text-muted-foreground">Relationships</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-cyan-400">5</p>
              <p className="text-sm text-muted-foreground">Entity Types</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-cyan-400">3</p>
              <p className="text-sm text-muted-foreground">External Sources</p>
            </div>
          </div>
        </motion.div>
      </div>
    </main>
  )
}
