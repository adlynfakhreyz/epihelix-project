import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Utility functions for EpiHelix
 */

/**
 * Combine class names conditionally with tailwind-merge
 * @param  {...any} inputs - Class names
 * @returns {string} Combined class names
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

/**
 * Format date to readable string
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted date
 */
export function formatDate(date) {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

/**
 * Debounce function calls
 * @param {Function} fn - Function to debounce
 * @param {number} delay - Delay in ms
 * @returns {Function} Debounced function
 */
export function debounce(fn, delay = 300) {
  let timeoutId
  return function (...args) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn.apply(this, args), delay)
  }
}

/**
 * Format large numbers with commas
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
export function formatNumber(num) {
  if (!num && num !== 0) return ''
  return num.toLocaleString()
}
