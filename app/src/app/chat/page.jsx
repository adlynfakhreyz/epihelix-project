'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Send, Sparkles, User, Bot, Trash2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useChat } from '@/hooks/useChat'

export default function ChatPage() {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  
  const { 
    sessionId, 
    messages, 
    send, 
    clear, 
    reset, 
    isLoading, 
    error,
    isReady 
  } = useChat()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  function handleSend() {
    if (!input.trim() || isLoading || !isReady) return

    const messageToSend = input.trim()
    setInput('')
    send(messageToSend)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleClearSession = () => {
    reset()
  }

  // Prevent hydration issues - show loading until client ready
  if (!isReady) {
    return (
      <div className="flex flex-col h-[calc(100vh-8rem)] items-center justify-center">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center animate-pulse">
          <Sparkles className="h-5 w-5 text-white" />
        </div>
        <p className="mt-4 text-muted-foreground">Loading chat...</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] -mx-6 sm:-mx-8 lg:-mx-12 -my-6 sm:-my-8 lg:-my-12">
      {/* Header */}
      <div className="border-b border-border/50 px-4 py-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-foreground">EpiHelix AI Assistant</h1>
              <p className="text-xs text-muted-foreground">Powered by RAG & Knowledge Graph</p>
            </div>
          </div>
          {messages.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClearSession}
              className="text-muted-foreground hover:text-foreground"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Clear Chat
            </Button>
          )}
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-8">
        <div className="max-w-5xl mx-auto">
          {/* Empty State */}
          {messages.length === 0 && !isLoading && (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-cyan-500/20 to-purple-600/20 flex items-center justify-center mb-6">
                <Sparkles className="h-10 w-10 text-cyan-400" />
              </div>
              <h2 className="text-2xl font-bold text-foreground mb-3">
                How can I help you today?
              </h2>
              <p className="text-muted-foreground max-w-md mb-8">
                Ask me anything about pandemics, diseases, outbreaks, or historical data. I&apos;ll search the knowledge graph to provide accurate answers.
              </p>

              {/* Suggested Prompts */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl">
                {[
                  'What is COVID-19?',
                  'Tell me about Malaria outbreaks',
                  'Which countries had the most cholera cases?',
                  'Compare tuberculosis and HIV/AIDS',
                ].map((prompt, idx) => (
                  <button
                    key={`prompt-${idx}`}
                    onClick={() => setInput(prompt)}
                    className="p-4 text-left bg-card/80 backdrop-blur-xl border border-border/50 rounded-xl 
                             hover:border-cyan-500/50 hover:shadow-lg hover:shadow-cyan-500/10 
                             transition-all duration-200"
                  >
                    <span className="hover:text-cyan-400 transition-colors duration-200">
                      {prompt}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400">
              Error: {error.message || 'Something went wrong. Please try again.'}
            </div>
          )}

          {/* Chat Messages */}
          {messages.map((msg, idx) => (
            <div
              key={`msg-${idx}`}
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
                        {msg.sources.map((source, sourceIdx) => (
                          <Badge
                            key={`source-${idx}-${sourceIdx}`}
                            variant="outline"
                            className="hover:bg-cyan-500/10 hover:border-cyan-500/50 transition-colors"
                          >
                            {source.label} {source.type && `(${source.type})`}
                          </Badge>
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
            </div>
          ))}

          {/* Loading Indicator */}
          {isLoading && (
            <div className="flex gap-4 mb-6">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                <Bot className="h-4 w-4 text-white" />
              </div>
              <div className="bg-card/80 backdrop-blur-xl border border-border/50 rounded-2xl p-4">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:0.1s]" />
                  <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                  <span className="ml-2 text-sm text-muted-foreground">Searching knowledge graph...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Bar */}
      <div className="border-t border-border/50 px-4 py-4 flex-shrink-0">
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
                disabled={isLoading}
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
              disabled={isLoading || !input.trim()}
              size="lg"
              className="rounded-full w-12 h-12 flex-shrink-0"
            >
              <Send className="h-5 w-5" />
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2 text-center">
            AI responses are generated from the knowledge graph using Groq LLM. Always verify important information.
          </p>
        </div>
      </div>
    </div>
  )
}