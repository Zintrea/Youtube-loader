import { render, screen } from '@testing-library/react'
import Home from '../page'

vi.mock('next/image', () => ({
  default: (props: any) => <img {...props} />,
}))

describe('Home Page', () => {
  it('renders the main heading', () => {
    render(<Home />)
    const heading = screen.getByRole('heading', {
      name: /to get started, edit the page\.tsx file\./i,
    })
    expect(heading).toBeInTheDocument()
  })

  it('renders the Next.js logo', () => {
    render(<Home />)
    const logo = screen.getByAltText(/next\.js logo/i)
    expect(logo).toBeInTheDocument()
  })
})
