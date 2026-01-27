import React from 'react'
import './Card.css'

/**
 * Component Card de hien thi noi dung trong cac container
 * @param {Object} props - Cac thuoc tinh cua card
 * @param {string} props.className - CSS class bo sung
 * @param {boolean} props.hover - Co hieu ung hover khong
 * @param {boolean} props.shadow - Co box shadow khong
 * @param {string} props.padding - Kich thuoc padding: 'sm', 'md', 'lg'
 * @param {React.ReactNode} props.children - Noi dung ben trong card
 * @param {Function} props.onClick - Ham xu ly su kien click
 */
const Card = ({ 
  className = '', 
  hover = false, 
  shadow = true, 
  padding = 'md', 
  children, 
  onClick,
  ...props 
}) => {
  // Tao cac class CSS dua tren props
  const cardClasses = [
    'card',
    shadow && 'card-shadow',
    hover && 'card-hover',
    `card-padding-${padding}`,
    onClick && 'card-clickable',
    className
  ].filter(Boolean).join(' ')

  const CardElement = onClick ? 'button' : 'div'

  return (
    <CardElement
      className={cardClasses}
      onClick={onClick}
      {...props}
    >
      {children}
    </CardElement>
  )
}

/**
 * Component CardHeader - Phan dau card
 */
export const CardHeader = ({ className = '', children, ...props }) => {
  return (
    <div className={`card-header ${className}`} {...props}>
      {children}
    </div>
  )
}

/**
 * Component CardBody - Phan noi dung chinh cua card
 */
export const CardBody = ({ className = '', children, ...props }) => {
  return (
    <div className={`card-body ${className}`} {...props}>
      {children}
    </div>
  )
}

/**
 * Component CardFooter - Phan cuoi card
 */
export const CardFooter = ({ className = '', children, ...props }) => {
  return (
    <div className={`card-footer ${className}`} {...props}>
      {children}
    </div>
  )
}

export default Card