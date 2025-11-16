'use client'

import Link from 'next/link'
import { Github, Twitter, Mail } from 'lucide-react'

/**
 * Footer links configuration
 */
const footerLinks = {
  product: [
    { href: '/search', label: 'Search' },
    { href: '/query', label: 'Query Console' },
    { href: '/chat', label: 'Chat' },
  ],
  resources: [
    { href: '/docs', label: 'Documentation' },
    { href: '/api', label: 'API Reference' },
    { href: '/about', label: 'About' },
  ],
  legal: [
    { href: '/privacy', label: 'Privacy' },
    { href: '/terms', label: 'Terms' },
  ],
}

const socialLinks = [
  { href: 'https://github.com', icon: Github, label: 'GitHub' },
  { href: 'https://twitter.com', icon: Twitter, label: 'Twitter' },
  { href: 'mailto:contact@epihelix.example.org', icon: Mail, label: 'Email' },
]

/**
 * Footer component with links and credits (compact version)
 */
export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="border-t border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
        {/* Single Row Layout */}
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          {/* Left: Brand & Copyright */}
          <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-4">
            <h3 className="font-bold text-sm bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
              EpiHelix
            </h3>
            <span className="hidden sm:inline text-muted-foreground text-xs">•</span>
            <p className="text-xs text-muted-foreground">
              © {currentYear} Pandemic Insights Explorer
            </p>
          </div>

          {/* Center: Quick Links */}
          <div className="flex flex-wrap justify-center items-center gap-x-6 gap-y-2 text-xs">
            {footerLinks.product.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                {link.label}
              </Link>
            ))}
            <span className="text-muted-foreground hidden sm:inline">•</span>
            {footerLinks.resources.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                {link.label}
              </Link>
            ))}
            <span className="text-muted-foreground hidden sm:inline">•</span>
            {footerLinks.legal.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Right: Social Links */}
          <div className="flex items-center gap-3">
            {socialLinks.map((social) => {
              const Icon = social.icon
              return (
                <a
                  key={social.label}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                  aria-label={social.label}
                >
                  <Icon className="h-4 w-4" />
                </a>
              )
            })}
          </div>
        </div>
      </div>
    </footer>
  )
}
