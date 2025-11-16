'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Search, Database, Network, Bot, Sparkles, Terminal, MessageCircle } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { fadeIn, staggerChildren } from '@/lib/animations'

// Placeholders array outside component to prevent recreation on each render
const placeholders = [
  '1918 Spanish Flu',
  'COVID-19 symptoms',
  'pandemic timeline',
  'Influenza A virus',
  'vaccine development',
]

export default function Home() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState('')
  const [semantic, setSemantic] = useState(false)
  const [placeholderIndex, setPlaceholderIndex] = useState(0)
  const [displayedText, setDisplayedText] = useState('')
  const [isDeleting, setIsDeleting] = useState(false)

  // Typewriter effect for placeholder
  useEffect(() => {
    const currentPlaceholder = placeholders[placeholderIndex]
    const typingSpeed = isDeleting ? 50 : 100
    const pauseTime = isDeleting ? 500 : 2000

    if (!isDeleting && displayedText === currentPlaceholder) {
      setTimeout(() => setIsDeleting(true), pauseTime)
      return
    }

    if (isDeleting && displayedText === '') {
      setIsDeleting(false)
      setPlaceholderIndex((prev) => (prev + 1) % placeholders.length)
      return
    }

    const timeout = setTimeout(() => {
      setDisplayedText(
        isDeleting
          ? currentPlaceholder.substring(0, displayedText.length - 1)
          : currentPlaceholder.substring(0, displayedText.length + 1)
      )
    }, typingSpeed)

    return () => clearTimeout(timeout)
  }, [displayedText, isDeleting, placeholderIndex])

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}&semantic=${semantic}`)
    }
  }
  const features = [
    {
      icon: Database,
      title: 'Integrated Knowledge Graph',
      description: 'Internal pandemic data merged with external sources (Wikidata, DBpedia)',
      color: 'from-cyan-500 to-blue-500',
    },
    {
      icon: Sparkles,
      title: 'AI-Powered Search',
      description: 'Semantic search with vector embeddings and intelligent reranking',
      color: 'from-purple-500 to-pink-500',
    },
    {
      icon: Network,
      title: 'Interactive Visualizations',
      description: 'Explore graph networks, timeseries charts, and entity relationships',
      color: 'from-orange-500 to-red-500',
    },
    {
      icon: Terminal,
      title: 'Query Console',
      description: 'Execute custom SPARQL or Cypher queries directly on the knowledge graph',
      color: 'from-emerald-500 to-teal-500',
    },
    {
      icon: Bot,
      title: 'RAG Chatbot',
      description: 'Ask questions and get answers backed by knowledge graph sources',
      color: 'from-green-500 to-lime-500',
    },
  ]

  return (
    <main className="flex-1">
      <div className="container mx-auto px-6 sm:px-8 lg:px-12 py-12 md:py-16" style={{ maxWidth: '1400px' }}>
        {/* Hero Section with Google-style Search */}
        <motion.div {...fadeIn} className="text-center mb-16 md:mb-24">
          <motion.h1
            className="text-6xl sm:text-7xl md:text-8xl font-bold mb-8 tracking-tight"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <span className="bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 bg-clip-text text-transparent drop-shadow-lg inline-block">
              EpiHelix
            </span>
          </motion.h1>

          <motion.p
            className="text-base sm:text-lg text-muted-foreground mb-3 max-w-3xl mx-auto px-4 leading-relaxed font-medium"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
          >
            A comprehensive knowledge graph application that integrates historical pandemic data 
            with external knowledge bases like Wikidata and DBpedia.
          </motion.p>
          <motion.p
            className="text-sm sm:text-base text-muted-foreground/80 mb-12 max-w-3xl mx-auto px-4 leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
          >
            Explore pandemic-related entities, discover relationships through interactive visualizations, 
            and leverage AI-powered semantic search to find insights across integrated data sources.
          </motion.p>

          {/* Divider Line - Same width as others */}
          <motion.div
            className="flex items-center justify-center mb-12"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.6, duration: 0.6 }}
          >
            <div className="h-px flex-1 max-w-xs bg-gradient-to-r from-transparent via-border to-border"></div>
            <div className="mx-4 text-muted-foreground/50">✦</div>
            <div className="h-px flex-1 max-w-xs bg-gradient-to-l from-transparent via-border to-border"></div>
          </motion.div>

          {/* "Start Exploring" heading - Sharp underline like Powerful Features */}
          <motion.div
            className="relative inline-block mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.6 }}
          >
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight relative">
              <span className="relative inline-block">
                <span className="bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
                  Start Exploring
                </span>
                <div className="absolute -bottom-2 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-cyan-500 to-transparent"></div>
              </span>
            </h2>
          </motion.div>

          {/* Google-style Search Bar with Typewriter */}
          <form onSubmit={handleSearch} className="max-w-3xl mx-auto mb-2">
            <div className="relative group">
              <Search className="absolute left-6 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-cyan-400 transition-colors z-10" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={`${displayedText}|`}
                suppressHydrationWarning
                className="w-full pl-14 pr-16 py-5 rounded-full bg-card/90 backdrop-blur-xl border-2 border-border/50 
                         text-foreground placeholder:text-muted-foreground text-lg
                         focus:outline-none focus:border-cyan-500/50 focus:ring-4 focus:ring-cyan-500/20
                         hover:border-border hover:shadow-xl hover:shadow-cyan-500/10
                         transition-all duration-200"
              />
            </div>
          </form>
          
          {/* Semantic Search Toggle */}
          <motion.div
            className="flex items-center justify-center gap-3 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.0, duration: 0.6 }}
          >
            <button
              type="button"
              onClick={() => setSemantic(!semantic)}
              className={`flex items-center gap-2 px-4 py-2 rounded-full border transition-all ${
                semantic
                  ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-400'
                  : 'bg-card/50 border-border/50 text-muted-foreground hover:border-border'
              }`}
            >
              <Sparkles className="h-4 w-4" />
              <span className="text-sm font-medium">
                {semantic ? 'Vector Search' : 'Keyword Search'}
              </span>
            </button>
          </motion.div>

          {/* Quick Access Buttons */}
          <div className="flex flex-wrap items-center justify-center gap-3">
            <Link href="/search">
              <Button size="lg" className="gap-2">
                <Search className="h-4 w-4" />
                Search Database
              </Button>
            </Link>
            <Link href="/query">
              <Button size="lg" variant="outline" className="gap-2">
                <Terminal className="h-4 w-4" />
                Query Console
              </Button>
            </Link>
            <Link href="/chat">
              <Button size="lg" variant="outline" className="gap-2">
                <MessageCircle className="h-4 w-4" />
                AI Assistant
              </Button>
            </Link>
          </div>
        </motion.div>

        {/* Divider Line */}
        <motion.div
          className="flex items-center justify-center mb-16 md:mb-20"
          initial={{ opacity: 0, scale: 0.8 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <div className="h-px flex-1 max-w-xs bg-gradient-to-r from-transparent via-border to-border"></div>
          <div className="mx-4 text-muted-foreground/50">✦</div>
          <div className="h-px flex-1 max-w-xs bg-gradient-to-l from-transparent via-border to-border"></div>
        </motion.div>

        {/* Features */}
        <motion.div {...fadeIn} className="mb-12 md:mb-16">
          <div className="text-center mb-10">
            <motion.h2
              className="text-2xl sm:text-3xl font-bold text-foreground mb-4"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <span className="relative inline-block">
                Powerful Features
                <div className="absolute -bottom-1 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-cyan-500 to-transparent"></div>
              </span>
            </motion.h2>
            <motion.p
              className="text-sm sm:text-base text-muted-foreground px-4"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2, duration: 0.6 }}
            >
              Built with <span className="text-cyan-400 font-semibold">cutting-edge technologies</span> for pandemic research
            </motion.p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {features.slice(0, 3).map((feature, idx) => {
              const Icon = feature.icon
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: idx * 0.1, duration: 0.5 }}
                >
                  <Card className="h-full hover:border-cyan-500/50 transition-all hover:shadow-lg hover:shadow-cyan-500/10 group">
                    <CardContent className="p-6 text-center">
                      <div className={`w-14 h-14 mx-auto rounded-full bg-gradient-to-br ${feature.color} p-3 mb-4 group-hover:scale-110 transition-transform shadow-lg`}>
                        <Icon className="w-full h-full text-white" />
                      </div>
                      <h4 className="font-semibold text-foreground mb-2 text-sm">
                        {feature.title}
                      </h4>
                      <p className="text-xs text-muted-foreground leading-relaxed">
                        {feature.description}
                      </p>
                    </CardContent>
                  </Card>
                </motion.div>
              )
            })}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {features.slice(3).map((feature, idx) => {
              const Icon = feature.icon
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: (idx + 3) * 0.1, duration: 0.5 }}
                >
                  <Card className="h-full hover:border-cyan-500/50 transition-all hover:shadow-lg hover:shadow-cyan-500/10 group">
                    <CardContent className="p-6 text-center">
                      <div className={`w-14 h-14 mx-auto rounded-full bg-gradient-to-br ${feature.color} p-3 mb-4 group-hover:scale-110 transition-transform shadow-lg`}>
                        <Icon className="w-full h-full text-white" />
                      </div>
                      <h4 className="font-semibold text-foreground mb-2 text-sm">
                        {feature.title}
                      </h4>
                      <p className="text-xs text-muted-foreground leading-relaxed">
                        {feature.description}
                      </p>
                    </CardContent>
                  </Card>
                </motion.div>
              )
            })}
          </div>
        </motion.div>

        {/* Divider Line */}
        <motion.div
          className="flex items-center justify-center mb-12 md:mb-16"
          initial={{ opacity: 0, scale: 0.8 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <div className="h-px flex-1 max-w-xs bg-gradient-to-r from-transparent via-border to-border"></div>
          <div className="mx-4 text-muted-foreground/50">✦</div>
          <div className="h-px flex-1 max-w-xs bg-gradient-to-l from-transparent via-border to-border"></div>
        </motion.div>

        {/* Combined Section: Data Sources Slider + Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="space-y-8"
        >
          {/* Data Sources Heading */}
          <h3 className="text-center text-sm font-semibold text-muted-foreground tracking-wider uppercase">
            Integrated Data Sources
          </h3>
          
          {/* Infinite Scroll Container */}
          <div className="relative overflow-hidden">
            {/* Sliding Content */}
            <motion.div
              className="flex gap-12 items-center py-6"
              animate={{
                x: [0, -1800],
              }}
              transition={{
                x: {
                  repeat: Infinity,
                  repeatType: "loop",
                  duration: 45,
                  ease: "linear",
                },
              }}
            >
              {/* First Set */}
              {[
                { name: 'Wikidata', logo: 'https://upload.wikimedia.org/wikipedia/commons/6/66/Wikidata-logo-en.svg' },
                { name: 'DBpedia', logo: 'https://www.dbpedia.org/wp-content/uploads/2020/09/dbpedia-org-logo.png' },
                { name: 'Kaggle', logo: 'https://www.kaggle.com/static/images/site-logo.svg' },
                { name: 'WHO', logo: 'https://www.who.int/images/default-source/fallback/header-logos/h-logo-blue1820eae93c154e37b2588ab90fdbc17e.svg?sfvrsn=aaed4f35_20' },
                { name: 'CDC', logo: 'https://logos-world.net/wp-content/uploads/2021/09/CDC-Logo.png' },
                { name: 'PubMed', logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/US-NLM-PubMed-Logo.svg/512px-US-NLM-PubMed-Logo.svg.png' },
                { name: 'NCBI', logo: 'https://www.ncbi.nlm.nih.gov/corehtml/logo100.gif' },
              ].map((source, idx) => (
                <div
                  key={`source-1-${idx}`}
                  className="flex-shrink-0 group"
                  style={{ minWidth: '140px' }}
                >
                  <div className="flex flex-col items-center gap-3">
                    <img
                      src={source.logo}
                      alt={source.name}
                      className="h-16 w-auto object-contain opacity-70 group-hover:opacity-100 group-hover:scale-110 transition-all duration-300"
                    />
                    <span className="text-xs font-medium text-muted-foreground group-hover:text-cyan-400 transition-colors">
                      {source.name}
                    </span>
                  </div>
                </div>
              ))}
              
              {/* Duplicate Set for Seamless Loop */}
              {[
                { name: 'Wikidata', logo: 'https://upload.wikimedia.org/wikipedia/commons/6/66/Wikidata-logo-en.svg' },
                { name: 'DBpedia', logo: 'https://www.dbpedia.org/wp-content/uploads/2020/09/dbpedia-org-logo.png' },
                { name: 'Kaggle', logo: 'https://www.kaggle.com/static/images/site-logo.svg' },
                { name: 'WHO', logo: 'https://www.who.int/images/default-source/fallback/header-logos/h-logo-blue1820eae93c154e37b2588ab90fdbc17e.svg?sfvrsn=aaed4f35_20' },
                { name: 'CDC', logo: 'https://logos-world.net/wp-content/uploads/2021/09/CDC-Logo.png' },
                { name: 'PubMed', logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/US-NLM-PubMed-Logo.svg/512px-US-NLM-PubMed-Logo.svg.png' },
                { name: 'NCBI', logo: 'https://www.ncbi.nlm.nih.gov/corehtml/logo100.gif' },
              ].map((source, idx) => (
                <div
                  key={`source-2-${idx}`}
                  className="flex-shrink-0 group"
                  style={{ minWidth: '140px' }}
                >
                  <div className="flex flex-col items-center gap-3">
                    <img
                      src={source.logo}
                      alt={source.name}
                      className="h-16 w-auto object-contain opacity-70 group-hover:opacity-100 group-hover:scale-110 transition-all duration-300"
                    />
                    <span className="text-xs font-medium text-muted-foreground group-hover:text-cyan-400 transition-colors">
                      {source.name}
                    </span>
                  </div>
                </div>
              ))}
            </motion.div>
          </div>

          {/* Stats Card */}
          <Card className="bg-gradient-to-br from-cyan-500/10 via-purple-500/10 to-pink-500/10 border-cyan-500/20 shadow-lg">
            <CardContent className="p-6 md:p-8">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 md:gap-8 text-center">
                <div className="group hover:scale-105 transition-transform">
                  <div className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-cyan-400 to-cyan-600 bg-clip-text text-transparent mb-2">10K+</div>
                  <div className="text-xs sm:text-sm text-muted-foreground">Entities in Knowledge Graph</div>
                </div>
                <div className="group hover:scale-105 transition-transform">
                  <div className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-purple-400 to-purple-600 bg-clip-text text-transparent mb-2">50+</div>
                  <div className="text-xs sm:text-sm text-muted-foreground">Integrated Data Sources</div>
                </div>
                <div className="group hover:scale-105 transition-transform">
                  <div className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-pink-400 to-pink-600 bg-clip-text text-transparent mb-2">100K+</div>
                  <div className="text-xs sm:text-sm text-muted-foreground">Relationships Mapped</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </main>
  )
}

