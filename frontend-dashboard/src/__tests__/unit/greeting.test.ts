import { describe, expect, it } from 'vitest'
import { getGreeting } from '../../components/dashboard/greeting'

function atHour(hour: number): Date {
  return new Date(2024, 0, 1, hour, 0, 0)
}

describe('getGreeting', () => {
  it.each([
    [0, 'Good night'],
    [4, 'Good night'],
    [5, 'Good morning'],
    [11, 'Good morning'],
    [12, 'Good afternoon'],
    [16, 'Good afternoon'],
    [17, 'Good evening'],
    [20, 'Good evening'],
    [21, 'Good night'],
    [23, 'Good night'],
  ])('at hour %i returns "%s"', (hour, expected) => {
    expect(getGreeting(atHour(hour))).toBe(expected)
  })
})
