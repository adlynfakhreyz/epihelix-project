'use client'

import React, { useEffect, useRef } from 'react'

/**
 * Animated graph background with particles and connections
 * Creates a moving network visualization behind content
 */
export function AnimatedGraphBackground() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    let animationFrameId
    let particles = []

    // Particle class with pulsing effect
    class Particle {
      constructor() {
        this.x = Math.random() * canvas.width
        this.y = Math.random() * canvas.height
        this.vx = (Math.random() - 0.5) * 0.5
        this.vy = (Math.random() - 0.5) * 0.5
        this.baseRadius = Math.random() * 1.5 + 1.5 // Smaller: 1.5-3px
        this.radius = this.baseRadius
        this.opacity = Math.random() * 0.4 + 0.3
        this.pulseSpeed = Math.random() * 0.02 + 0.01
        this.pulsePhase = Math.random() * Math.PI * 2
      }

      update() {
        this.x += this.vx
        this.y += this.vy

        // Wrap around edges (infinite space effect)
        if (this.x < -50) this.x = canvas.width + 50
        if (this.x > canvas.width + 50) this.x = -50
        if (this.y < -50) this.y = canvas.height + 50
        if (this.y > canvas.height + 50) this.y = -50

        // Pulsing effect
        this.pulsePhase += this.pulseSpeed
        this.radius = this.baseRadius + Math.sin(this.pulsePhase) * 1.5
      }

      draw() {
        // Draw outer glow
        const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.radius * 3)
        gradient.addColorStop(0, `rgba(34, 193, 195, ${this.opacity * 0.3})`)
        gradient.addColorStop(0.5, `rgba(34, 193, 195, ${this.opacity * 0.1})`)
        gradient.addColorStop(1, 'rgba(34, 193, 195, 0)')
        
        ctx.fillStyle = gradient
        ctx.beginPath()
        ctx.arc(this.x, this.y, this.radius * 3, 0, Math.PI * 2)
        ctx.fill()

        // Draw main particle
        ctx.beginPath()
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(34, 193, 195, ${this.opacity})`
        ctx.fill()
      }
    }

    // Set canvas size and reinitialize particles on resize
    const resizeCanvas = () => {
      const oldWidth = canvas.width || window.innerWidth
      const oldHeight = canvas.height || window.innerHeight
      const newWidth = window.innerWidth
      const newHeight = window.innerHeight
      
      // Update canvas dimensions first
      canvas.width = newWidth
      canvas.height = newHeight
      
      // Scale existing particles to new dimensions
      const scaleX = newWidth / oldWidth
      const scaleY = newHeight / oldHeight
      
      particles.forEach(particle => {
        particle.x *= scaleX
        particle.y *= scaleY
      })
      
      // Adjust particle count based on new screen size
      const targetCount = Math.min(200, Math.floor((newWidth * newHeight) / 10000))
      if (particles.length < targetCount) {
        // Add more particles
        while (particles.length < targetCount) {
          particles.push(new Particle())
        }
      } else if (particles.length > targetCount) {
        // Remove excess particles
        particles.splice(targetCount)
      }
    }

    // Initial setup
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
    
    // Initialize particles
    const particleCount = Math.min(200, Math.floor((canvas.width * canvas.height) / 10000))
    for (let i = 0; i < particleCount; i++) {
      particles.push(new Particle())
    }

    window.addEventListener('resize', resizeCanvas)

    // Draw connections between nearby particles (more connected graph)
    const drawConnections = () => {
      const maxDistance = 300 // Increased for more connections

      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x
          const dy = particles[i].y - particles[j].y
          const distance = Math.sqrt(dx * dx + dy * dy)

          if (distance < maxDistance) {
            const opacity = (1 - distance / maxDistance) * 0.1 // Thicker edges
            ctx.beginPath()
            ctx.moveTo(particles[i].x, particles[i].y)
            ctx.lineTo(particles[j].x, particles[j].y)
            ctx.strokeStyle = `rgba(124, 92, 255, ${opacity})`
            ctx.lineWidth = 2 // Thicker lines
            ctx.stroke()
          }
        }
      }
    }

    // Animation loop
    const animate = () => {
      // Clear canvas completely (no trail effect, clean edge movement)
      ctx.fillStyle = 'rgba(11, 11, 13, 1)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // Draw connections first (so they appear behind particles)
      drawConnections()

      // Update and draw particles
      particles.forEach((particle) => {
        particle.update()
        particle.draw()
      })

      animationFrameId = requestAnimationFrame(animate)
    }

    animate()

    // Cleanup
    return () => {
      window.removeEventListener('resize', resizeCanvas)
      cancelAnimationFrame(animationFrameId)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 w-full h-full pointer-events-none"
      style={{ zIndex: 0 }}
    />
  )
}
