'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Send, Sparkles, User, Bot } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

export default function ChatPage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  async function handleSend() {
    if (!input.trim()) return

    const userMessage = { role: 'user', content: input }
    setMessages([...messages, userMessage])
    setInput('')
    setLoading(true)

    // Mock response
    setTimeout(() => {
      const assistantMessage = {
        role: 'assistant',
        content: `I understand you're asking about "${input}". This is a mock response. When the backend is ready, I'll provide real answers based on the knowledge graph using RAG (Retrieval-Augmented Generation).`,
        sources: [
          { id: 'disease:influenza_A', label: 'Influenza A' },
          { id: 'outbreak:1918_spanish_flu', label: '1918 Spanish Flu' },
        ],
      }
      setMessages((prev) => [...prev, assistantMessage])
      setLoading(false)
    }, 1500)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] -mx-6 sm:-mx-8 lg:-mx-12 -my-6 sm:-my-8 lg:-my-12">
      {/* Header */}
      <motion.div
        className="border-b border-border/50 px-4 py-4 flex-shrink-0"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-foreground">EpiHelix AI Assistant</h1>
            <p className="text-xs text-muted-foreground">Powered by RAG & Knowledge Graph</p>
          </div>
        </div>
      </motion.div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-8">
        <div className="max-w-5xl mx-auto">
          <AnimatePresence mode="popLayout">
            {messages.length === 0 && !loading && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="flex flex-col items-center justify-center min-h-[60vh] text-center"
              >
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-cyan-500/20 to-purple-600/20 flex items-center justify-center mb-6">
                  <Sparkles className="h-10 w-10 text-cyan-400" />
                </div>
                <motion.h2
                  className="text-2xl font-bold text-foreground mb-3"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2, duration: 0.6 }}
                >
                  How can I help you today?
                </motion.h2>
                <motion.p
                  className="text-muted-foreground max-w-md mb-8"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4, duration: 0.6 }}
                >
                  Ask me anything about pandemics, diseases, outbreaks, or historical data. I'll search the knowledge graph to provide accurate answers.
                </motion.p>

                {/* Suggested Prompts */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl">
                  {[
                    'Tell me about the 1918 Spanish Flu',
                    'What are the symptoms of Influenza A?',
                    'Show me COVID-19 outbreak data',
                    'Compare different pandemic responses',
                  ].map((prompt, idx) => (
                    <motion.button
                      key={idx}
                      onClick={() => setInput(prompt)}
                      className="p-4 text-left bg-card/80 backdrop-blur-xl border border-border/50 rounded-xl 
                               hover:border-cyan-500/50 hover:shadow-lg hover:shadow-cyan-500/10 
                               group"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.8 + (idx * 0.1), duration: 0.6 }}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <span className="group-hover:text-cyan-400 transition-colors duration-200">
                        {prompt}
                      </span>
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Chat Messages */}
            {messages.map((msg, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className={`flex gap-4 mb-6 ${msg.role === 'user' ? 'justify-end' : ''}`}
              >
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                    <Bot className="h-4 w-4 text-white" />
                  </div>
                )}

                <div className={`flex-1 max-w-3xl ${msg.role === 'user' ? 'flex justify-end' : ''}`}>
                  <div
                    className={`${
                      msg.role === 'user'
                        ? 'bg-cyan-500/20 border-cyan-500/30 ml-12'
                        : 'bg-card/80 backdrop-blur-xl border-border/50'
                    } border rounded-2xl p-4`}
                  >
                    <p className="text-foreground leading-relaxed whitespace-pre-wrap">
                      {msg.content}
                    </p>

                    {/* Sources */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-border/50">
                        <p className="text-xs text-muted-foreground mb-2 flex items-center gap-2">
                          <Sparkles className="h-3 w-3" />
                          Sources from Knowledge Graph:
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {msg.sources.map((source) => (
                            <a
                              key={source.id}
                              href={`/entity/${source.id}`}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              <Badge
                                variant="outline"
                                className="hover:bg-cyan-500/10 hover:border-cyan-500/50 transition-colors cursor-pointer"
                              >
                                {source.label}
                              </Badge>
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center flex-shrink-0">
                    <User className="h-4 w-4 text-muted-foreground" />
                  </div>
                )}
              </motion.div>
            ))}

            {/* Loading Indicator */}
            {loading && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-4 mb-6"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                  <Bot className="h-4 w-4 text-white" />
                </div>
                <div className="bg-card/80 backdrop-blur-xl border border-border/50 rounded-2xl p-4">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Bar - Sticky Bottom */}
      <motion.div
        className="border-t border-border/50 px-4 py-4 flex-shrink-0"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.6 }}
      >
        <div className="max-w-5xl mx-auto">
          <div className="flex items-end gap-3">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Ask me anything about pandemics..."
                rows={1}
                className="w-full px-4 py-3 pr-12 bg-card/60 backdrop-blur-md border-2 border-border/50 rounded-2xl text-foreground placeholder-muted-foreground 
                         focus:outline-none focus:border-cyan-500/50 focus:ring-4 focus:ring-cyan-500/20
                         resize-none max-h-32 text-base"
                disabled={loading}
                style={{
                  height: 'auto',
                  minHeight: '48px',
                }}
                onInput={(e) => {
                  e.target.style.height = 'auto'
                  e.target.style.height = e.target.scrollHeight + 'px'
                }}
              />
            </div>
            <Button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              size="lg"
              className="rounded-full w-12 h-12 flex-shrink-0"
            >
              <Send className="h-5 w-5" />
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2 text-center">
            AI responses are generated from the knowledge graph. Always verify important information.
          </p>
        </div>
      </motion.div>
    </div>
  )
}
