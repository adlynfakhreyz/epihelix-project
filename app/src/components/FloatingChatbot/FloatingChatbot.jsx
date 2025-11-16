'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { MessageCircle, X, Minimize2, Maximize2, ExternalLink } from 'lucide-react'
import { Button } from '@/components/ui/button'
import PropTypes from 'prop-types'

/**
 * Floating Chatbot Widget
 * Quick access chatbot that can be opened, minimized, and resized
 * Position: Fixed bottom-right corner
 */
export default function FloatingChatbot() {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [size, setSize] = useState('default') // 'default', 'large'

  const toggleOpen = () => {
    setIsOpen(!isOpen)
    setIsMinimized(false)
  }

  const toggleMinimize = () => {
    setIsMinimized(!isMinimized)
  }

  const toggleSize = () => {
    setSize(size === 'default' ? 'large' : 'default')
  }

  // Size configurations
  const sizeConfig = {
    default: 'w-96 h-[500px]',
    large: 'w-[600px] h-[700px]',
  }

  return (
    <>
      {/* Floating Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 260, damping: 20 }}
            className="fixed bottom-6 right-6 z-50"
          >
            <Button
              onClick={toggleOpen}
              size="lg"
              className="rounded-full w-16 h-16 shadow-lg hover:shadow-xl transition-shadow bg-gradient-to-br from-cyan-500 to-purple-600 hover:from-cyan-400 hover:to-purple-500"
              aria-label="Open chatbot"
            >
              <MessageCircle className="h-7 w-7" />
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chatbot Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ scale: 0.8, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.8, opacity: 0, y: 20 }}
            transition={{ type: 'spring', stiffness: 260, damping: 20 }}
            className={`fixed bottom-6 right-6 z-50 ${sizeConfig[size]} ${
              isMinimized ? 'h-14' : ''
            } bg-card/95 backdrop-blur-xl border border-border/50 rounded-2xl shadow-2xl overflow-hidden flex flex-col`}
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-cyan-500/10 to-purple-500/10 border-b border-border/50 px-4 py-3 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
                  <MessageCircle className="h-4 w-4 text-white" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-foreground">EpiHelix Assistant</h3>
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-xs text-muted-foreground">Online</span>
                  </div>
                </div>
              </div>

              {/* Controls */}
              <div className="flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={toggleSize}
                  aria-label={size === 'default' ? 'Enlarge' : 'Shrink'}
                >
                  <Maximize2 className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={toggleMinimize}
                  aria-label={isMinimized ? 'Restore' : 'Minimize'}
                >
                  <Minimize2 className="h-4 w-4" />
                </Button>
                <Link href="/chat">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    aria-label="Open in full page"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </Button>
                </Link>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={toggleOpen}
                  aria-label="Close"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Content */}
            {!isMinimized && (
              <div className="flex-1 flex items-center justify-center p-6">
                <div className="text-center">
                  <div className="text-4xl mb-4">💬</div>
                  <p className="text-muted-foreground mb-4">
                    Quick chat is coming soon!
                  </p>
                  <Link href="/chat">
                    <Button className="gap-2">
                      <ExternalLink className="h-4 w-4" />
                      Open Full Chat
                    </Button>
                  </Link>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
