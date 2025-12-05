'use client'

import React, { useState, useEffect, useMemo } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import {
  Search,
  Filter,
  X,
  ChevronLeft,
  ArrowRight,
  Globe,
  AlertCircle,
  Syringe,
  Building2,
  Network,
  Check,
  ChevronsUpDown,
} from 'lucide-react'
import { fadeIn } from '@/lib/animations'
import { cn } from '@/lib/utils'

const entityIcons = {
  country: Globe,
  disease: AlertCircle,
  outbreak: Network,
  vaccinationrecord: Syringe,
  organization: Building2,
}

export default function EntityListPage() {
  const params = useParams()
  const router = useRouter()
  const entityType = params.type

  const [entities, setEntities] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [filters, setFilters] = useState({})
  const [sortBy, setSortBy] = useState('name')
  const [availableFilters, setAvailableFilters] = useState([])
  const [openComboboxes, setOpenComboboxes] = useState({})

  // Fetch entities
  useEffect(() => {
    const fetchEntities = async () => {
      setLoading(true)
      try {
        const params = new URLSearchParams({
          type: entityType,
          search: searchQuery,
          sortBy,
          ...filters,
        })

        const response = await fetch(`/api/entities?${params}`)
        const data = await response.json()
        setEntities(data.entities || [])
        setAvailableFilters(data.availableFilters || [])
      } catch (error) {
        console.error('Failed to fetch entities:', error)
        setEntities([])
      } finally {
        setLoading(false)
      }
    }

    if (entityType) {
      fetchEntities()
    }
  }, [entityType, searchQuery, sortBy, filters])

  // Use entities from server (already filtered and sorted)
  const filteredEntities = entities

  const Icon = entityIcons[entityType?.toLowerCase()] || Globe

  const handleFilterChange = (filterKey, value) => {
    setFilters((prev) => ({
      ...prev,
      [filterKey]: value,
    }))
  }

  const clearFilter = (filterKey) => {
    setFilters((prev) => {
      const newFilters = { ...prev }
      delete newFilters[filterKey]
      return newFilters
    })
  }

  const clearAllFilters = () => {
    setFilters({})
    setSearchQuery('')
  }

  const hasActiveFilters = searchQuery || Object.keys(filters).length > 0

  return (
    <main className="flex-1 py-8 md:py-12">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        {/* Breadcrumb */}
        <nav className="mb-6 flex items-center gap-2 text-sm">
          <Link
            href="/entities"
            className="text-cyan-400 hover:text-cyan-300 transition-colors flex items-center gap-1"
          >
            <ChevronLeft className="h-4 w-4" />
            All Entity Types
          </Link>
        </nav>

        {/* Header */}
        <motion.div {...fadeIn} className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-lg bg-cyan-500/10">
              <Icon className="h-8 w-8 text-cyan-400" />
            </div>
            <div>
              <h1 className="text-3xl md:text-4xl font-bold capitalize">
                {entityType} Entities
              </h1>
              <p className="text-muted-foreground mt-1">
                {filteredEntities.length} {filteredEntities.length === 1 ? 'entity' : 'entities'} found
              </p>
            </div>
          </div>
        </motion.div>

        {/* Search and Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="mb-6"
        >
          <Card>
            <CardContent className="p-6">
              <div className="space-y-4">
                {/* Search Bar */}
                <div className="flex gap-4 flex-col md:flex-row">
                  <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search by name, ID, or description..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Select value={sortBy} onValueChange={setSortBy}>
                    <SelectTrigger className="w-full md:w-48">
                      <SelectValue placeholder="Sort by..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="name">Name (A-Z)</SelectItem>
                      <SelectItem value="id">ID</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Property Filters */}
                {availableFilters.length > 0 && (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-sm font-medium">
                        <Filter className="h-4 w-4 text-cyan-400" />
                        Filters
                      </div>
                      {hasActiveFilters && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={clearAllFilters}
                          className="text-xs text-muted-foreground hover:text-cyan-400"
                        >
                          Clear All
                        </Button>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {availableFilters.slice(0, 6).map((filter) => (
                        <div key={filter.key} className="space-y-1.5">
                          <label className="text-xs font-medium text-muted-foreground">
                            {filter.label}
                          </label>
                          {filter.type === 'select' ? (
                            <Popover 
                              open={openComboboxes[filter.key]} 
                              onOpenChange={(open) => 
                                setOpenComboboxes(prev => ({...prev, [filter.key]: open}))
                              }
                            >
                              <PopoverTrigger asChild>
                                <Button
                                  variant="outline"
                                  role="combobox"
                                  className={cn(
                                    "w-full justify-between",
                                    !filters[filter.key] && "text-muted-foreground"
                                  )}
                                >
                                  {filters[filter.key] 
                                    ? filter.options?.find(o => o.value === filters[filter.key])?.label 
                                    : `All ${filter.label}`}
                                  <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                                </Button>
                              </PopoverTrigger>
                              <PopoverContent className="w-[200px] p-0">
                                <Command>
                                  <CommandInput placeholder={`Search ${filter.label.toLowerCase()}...`} />
                                  <CommandList>
                                    <CommandEmpty>No {filter.label.toLowerCase()} found.</CommandEmpty>
                                    <CommandGroup>
                                      <CommandItem
                                        key="all"
                                        value=""
                                        onSelect={() => {
                                          handleFilterChange(filter.key, '')
                                          setOpenComboboxes(prev => ({...prev, [filter.key]: false}))
                                        }}
                                      >
                                        <Check
                                          className={cn(
                                            "mr-2 h-4 w-4",
                                            !filters[filter.key] ? "opacity-100" : "opacity-0"
                                          )}
                                        />
                                        All {filter.label}
                                      </CommandItem>
                                      {filter.options?.map((option) => (
                                        <CommandItem
                                          key={option.value}
                                          value={option.value}
                                          onSelect={() => {
                                            handleFilterChange(filter.key, option.value)
                                            setOpenComboboxes(prev => ({...prev, [filter.key]: false}))
                                          }}
                                        >
                                          <Check
                                            className={cn(
                                              "mr-2 h-4 w-4",
                                              filters[filter.key] === option.value ? "opacity-100" : "opacity-0"
                                            )}
                                          />
                                          {option.label}
                                        </CommandItem>
                                      ))}
                                    </CommandGroup>
                                  </CommandList>
                                </Command>
                              </PopoverContent>
                            </Popover>
                          ) : (
                            <Input
                              placeholder={`Filter by ${filter.label.toLowerCase()}...`}
                              value={filters[filter.key] || ''}
                              onChange={(e) => handleFilterChange(filter.key, e.target.value)}
                            />
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Active Filters */}
                {Object.keys(filters).length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(filters).map(([key, value]) => {
                      const filter = availableFilters.find((f) => f.key === key)
                      return (
                        <Badge
                          key={key}
                          variant="secondary"
                          className="gap-1 pr-1"
                        >
                          {filter?.label}: {value}
                          <button
                            onClick={() => clearFilter(key)}
                            className="ml-1 rounded-full hover:bg-muted p-0.5"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </Badge>
                      )
                    })}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Entity List */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <Card key={i}>
                <CardContent className="p-6">
                  <div className="animate-pulse space-y-3">
                    <div className="h-6 bg-muted rounded w-3/4" />
                    <div className="h-4 bg-muted rounded w-1/2" />
                    <div className="h-4 bg-muted rounded w-full" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filteredEntities.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <Icon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-lg font-medium text-muted-foreground mb-2">
                No entities found
              </p>
              <p className="text-sm text-muted-foreground mb-4">
                Try adjusting your search or filters
              </p>
              {hasActiveFilters && (
                <Button variant="outline" onClick={clearAllFilters}>
                  Clear Filters
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredEntities.map((entity, index) => (
              <motion.div
                key={entity.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: Math.min(index * 0.05, 0.3) }}
              >
                <Link href={`/entity/${entity.id}`}>
                  <Card className="h-full hover:border-cyan-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/10 group cursor-pointer">
                    <CardHeader>
                      <div className="flex items-start justify-between mb-2">
                        <CardTitle className="text-lg group-hover:text-cyan-400 transition-colors flex-1">
                          {entity.label}
                        </CardTitle>
                        <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-cyan-400 group-hover:translate-x-1 transition-all flex-shrink-0 ml-2" />
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">
                          {entity.type}
                        </Badge>
                        <span className="text-xs text-muted-foreground font-mono">
                          {entity.id}
                        </span>
                      </div>
                    </CardHeader>
                    {entity.description && (
                      <CardContent>
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {entity.description}
                        </p>
                      </CardContent>
                    )}
                    {entity.properties && Object.keys(entity.properties).length > 0 && (
                      <CardContent className="pt-0">
                        <div className="flex flex-wrap gap-1.5">
                          {Object.entries(entity.properties)
                            .slice(0, 3)
                            .map(([key, value]) => (
                              <Badge
                                key={key}
                                variant="secondary"
                                className="text-xs"
                              >
                                {key}: {String(value).substring(0, 20)}
                                {String(value).length > 20 && '...'}
                              </Badge>
                            ))}
                        </div>
                      </CardContent>
                    )}
                  </Card>
                </Link>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </main>
  )
}
