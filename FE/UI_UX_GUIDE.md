# 🎨 HƯỚNG DẪN UI/UX VÀ CSS CHO AI LEARNING PLATFORM

> **Dự án:** AI Learning Platform - Frontend JavaScript Version  
> **Ngày tạo:** 8/11/2025  
> **Mục đích:** Hướng dẫn chi tiết về cách sử dụng CSS thuần, tổ chức components và tuân thủ design system

---

## 📋 MỤC LỤC

1. [Tổng quan Design System](#1-tổng-quan-design-system)
2. [Hệ thống CSS Variables](#2-hệ-thống-css-variables)
3. [Quy tắc viết CSS](#3-quy-tắc-viết-css)
4. [Component Architecture](#4-component-architecture)
5. [Layout Guidelines](#5-layout-guidelines)
6. [Typography System](#6-typography-system)
7. [Color Palette](#7-color-palette)
8. [Spacing System](#8-spacing-system)
9. [Responsive Design](#9-responsive-design)
10. [Animation Guidelines](#10-animation-guidelines)
11. [Accessibility Best Practices](#11-accessibility-best-practices)
12. [Performance Tips](#12-performance-tips)

---

## 1. TỔNG QUAN DESIGN SYSTEM

### 1.1 Nguyên tắc thiết kế

- **Đơn giản (Simplicity):** UI sạch sẽ, tập trung vào nội dung chính
- **Nhất quán (Consistency):** Sử dụng pattern và component thống nhất
- **Dễ tiếp cận (Accessibility):** Hỗ trợ đầy đủ cho người khuyết tật
- **Responsive:** Tương thích mọi thiết bị từ mobile đến desktop
- **Performance:** Tối ưu tốc độ tải và hiệu suất

### 1.2 Cấu trúc thư mục CSS

```
src/styles/
├── index.css          # CSS chính, variables, utilities
├── components/        # CSS riêng cho từng component
│   ├── Button.css
│   ├── Card.css
│   ├── Input.css
│   └── Modal.css
└── pages/            # CSS cho các pages
    ├── LandingPage.css
    ├── AuthPages.css
    └── ErrorPages.css
```

---

## 2. HỆ THỐNG CSS VARIABLES

### 2.1 Color Variables

```css
:root {
  /* Primary colors */
  --primary: #3b82f6;           /* Blue-500 */
  --primary-hover: #2563eb;     /* Blue-600 */
  --primary-light: #dbeafe;     /* Blue-100 */
  
  /* Status colors */
  --success: #10b981;           /* Green-500 */
  --success-light: #d1fae5;     /* Green-100 */
  --warning: #f59e0b;           /* Amber-500 */
  --warning-light: #fef3c7;     /* Amber-100 */
  --danger: #ef4444;            /* Red-500 */
  --danger-light: #fee2e2;      /* Red-100 */
  
  /* Neutral colors */
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-card: #ffffff;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
  --border-color: #e2e8f0;
  --border-light: #f1f5f9;
}

/* Dark theme */
[data-theme="dark"] {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-card: #1e293b;
  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
  --text-muted: #64748b;
  --border-color: #334155;
  --border-light: #475569;
}
```

### 2.2 Spacing Variables

```css
:root {
  --spacing-xs: 0.25rem;    /* 4px */
  --spacing-sm: 0.5rem;     /* 8px */
  --spacing-md: 1rem;       /* 16px */
  --spacing-lg: 1.5rem;     /* 24px */
  --spacing-xl: 2rem;       /* 32px */
  --spacing-2xl: 3rem;      /* 48px */
}
```

### 2.3 Typography Variables

```css
:root {
  --font-size-xs: 0.75rem;     /* 12px */
  --font-size-sm: 0.875rem;    /* 14px */
  --font-size-base: 1rem;      /* 16px */
  --font-size-lg: 1.125rem;    /* 18px */
  --font-size-xl: 1.25rem;     /* 20px */
  --font-size-2xl: 1.5rem;     /* 24px */
  --font-size-3xl: 1.875rem;   /* 30px */
  --font-size-4xl: 2.25rem;    /* 36px */
}
```

---

## 3. QUY TẮC VIẾT CSS

### 3.1 Naming Convention

**Sử dụng BEM (Block Element Modifier):**

```css
/* Block */
.card { }

/* Element */
.card-header { }
.card-body { }
.card-footer { }

/* Modifier */
.card-hover { }
.card-loading { }
.card-padding-lg { }
```

### 3.2 Cấu trúc CSS File

```css
/* 1. Component chính */
.component-name {
  /* Layout properties */
  display: flex;
  position: relative;
  
  /* Box model */
  width: 100%;
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  
  /* Visual properties */
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  
  /* Typography */
  font-size: var(--font-size-base);
  color: var(--text-primary);
  
  /* Others */
  transition: all var(--transition-fast);
}

/* 2. States */
.component-name:hover { }
.component-name:focus { }
.component-name:active { }
.component-name:disabled { }

/* 3. Modifiers */
.component-name-variant { }
.component-name-size-lg { }

/* 4. Child elements */
.component-name .child-element { }

/* 5. Responsive */
@media (max-width: 768px) {
  .component-name { }
}
```

### 3.3 CSS Best Practices

```css
/* ✅ ĐÚNG */
.button {
  /* Sử dụng logical properties */
  margin-inline: auto;
  padding-block: var(--spacing-sm);
  
  /* Sử dụng CSS variables */
  color: var(--text-primary);
  background-color: var(--primary);
  
  /* Transition hiệu quả */
  transition: background-color var(--transition-fast);
}


---

## 4. COMPONENT ARCHITECTURE

### 4.1 Component CSS Structure

Mỗi component nên có file CSS riêng và follow pattern này:

```css
/* components/ui/Button.css */

/* 1. Base styles */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

/* 2. Size variants */
.btn-sm { padding: var(--spacing-sm) var(--spacing-md); }
.btn-md { padding: var(--spacing-md) var(--spacing-lg); }
.btn-lg { padding: var(--spacing-lg) var(--spacing-xl); }

/* 3. Color variants */
.btn-primary { background-color: var(--primary); color: white; }
.btn-secondary { background-color: var(--bg-secondary); }
.btn-outline { background: transparent; border: 1px solid var(--primary); }

/* 4. States */
.btn:hover:not(.btn-disabled) { transform: translateY(-1px); }
.btn:active:not(.btn-disabled) { transform: translateY(0); }
.btn-disabled { opacity: 0.5; cursor: not-allowed; }

/* 5. Responsive */
@media (max-width: 640px) {
  .btn-lg { padding: var(--spacing-md) var(--spacing-lg); }
}
```

### 4.2 Component CSS Import

```jsx
// components/ui/Button.jsx
import React from 'react'
import './Button.css'  // Import CSS của chính component

const Button = ({ variant, size, children, ...props }) => {
  return (
    <button className={`btn btn-${variant} btn-${size}`} {...props}>
      {children}
    </button>
  )
}
```

---

## 5. LAYOUT GUIDELINES

### 5.1 Container System

```css
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

.container-sm { max-width: 640px; }
.container-lg { max-width: 1400px; }
```

### 5.2 Grid System

```css
.grid {
  display: grid;
  gap: var(--spacing-md);
}

.grid-cols-1 { grid-template-columns: repeat(1, 1fr); }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
.grid-cols-4 { grid-template-columns: repeat(4, 1fr); }

/* Responsive grid */
.grid-responsive {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}
```

### 5.3 Flexbox Utilities

```css
.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.gap-md { gap: var(--spacing-md); }
```

---

## 6. TYPOGRAPHY SYSTEM

### 6.1 Heading Hierarchy

```css
h1, h2, h3, h4, h5, h6 {
  font-weight: 600;
  line-height: 1.2;
  color: var(--text-primary);
  margin-bottom: var(--spacing-md);
}

h1 { font-size: var(--font-size-4xl); }
h2 { font-size: var(--font-size-3xl); }
h3 { font-size: var(--font-size-2xl); }
h4 { font-size: var(--font-size-xl); }
h5 { font-size: var(--font-size-lg); }
h6 { font-size: var(--font-size-base); }
```

### 6.2 Text Utilities

```css
.text-xs { font-size: var(--font-size-xs); }
.text-sm { font-size: var(--font-size-sm); }
.text-base { font-size: var(--font-size-base); }
.text-lg { font-size: var(--font-size-lg); }

.font-medium { font-weight: 500; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }

.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }
```

---

## 7. COLOR PALETTE

### 7.1 Semantic Colors

| Tên | Giá trị | Sử dụng |
|-----|---------|---------|
| `--primary` | `#3b82f6` | Primary actions, links |
| `--success` | `#10b981` | Success states, confirmations |
| `--warning` | `#f59e0b` | Warnings, cautions |
| `--danger` | `#ef4444` | Errors, destructive actions |

### 7.2 Neutral Colors

| Tên | Light | Dark | Sử dụng |
|-----|-------|------|---------|
| `--bg-primary` | `#ffffff` | `#0f172a` | Main background |
| `--bg-secondary` | `#f8fafc` | `#1e293b` | Secondary background |
| `--text-primary` | `#1e293b` | `#f8fafc` | Primary text |
| `--text-secondary` | `#64748b` | `#cbd5e1` | Secondary text |

---

## 8. SPACING SYSTEM

### 8.1 Spacing Scale

```css
/* Spacing utilities */
.m-0 { margin: 0; }
.m-sm { margin: var(--spacing-sm); }
.m-md { margin: var(--spacing-md); }
.m-lg { margin: var(--spacing-lg); }

.p-0 { padding: 0; }
.p-sm { padding: var(--spacing-sm); }
.p-md { padding: var(--spacing-md); }
.p-lg { padding: var(--spacing-lg); }

/* Directional spacing */
.px-md { padding-left: var(--spacing-md); padding-right: var(--spacing-md); }
.py-md { padding-top: var(--spacing-md); padding-bottom: var(--spacing-md); }
```

---

## 9. RESPONSIVE DESIGN

### 9.1 Breakpoints

```css
/* Mobile first approach */
@media (min-width: 640px) {  /* sm */
  .sm\:grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 768px) {  /* md */
  .md\:grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
}

@media (min-width: 1024px) { /* lg */
  .lg\:grid-cols-4 { grid-template-columns: repeat(4, 1fr); }
}
```

### 9.2 Responsive Patterns

```css
/* Container queries (khi supported) */
@container (min-width: 400px) {
  .card { padding: var(--spacing-lg); }
}

/* Responsive typography */
.title {
  font-size: clamp(1.5rem, 4vw, 2.25rem);
}

/* Responsive spacing */
.section {
  padding: clamp(2rem, 5vw, 4rem) 0;
}
```

---

## 10. ANIMATION GUIDELINES

### 10.1 Transition Variables

```css
:root {
  --transition-fast: 150ms ease-in-out;
  --transition-normal: 250ms ease-in-out;
  --transition-slow: 350ms ease-in-out;
}
```

### 10.2 Common Animations

```css
/* Fade in */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Slide up */
@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

/* Usage */
.animate-fade-in { animation: fadeIn var(--transition-normal) ease-out; }
.animate-slide-up { animation: slideUp var(--transition-normal) ease-out; }
```

### 10.3 Hover Effects

```css
.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.hover-scale:hover {
  transform: scale(1.02);
}
```

---

## 11. ACCESSIBILITY BEST PRACTICES

### 11.1 Focus States

```css
/* Custom focus styles */
*:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

.btn:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}
```

### 11.2 Color Contrast

- Đảm bảo contrast ratio tối thiểu 4.5:1 cho text thông thường
- Contrast ratio tối thiểu 3:1 cho text lớn (18px+)
- Sử dụng tools như [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

### 11.3 Screen Reader Support

```css
/* Screen reader only content */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

---

## 12. PERFORMANCE TIPS

### 12.1 CSS Optimization

```css
/* ✅ Efficient selectors */
.btn { }
.card-header { }


### 12.2 Critical CSS

- Inline critical CSS trong `<head>`
- Lazy load non-critical CSS
- Sử dụng `preload` cho important stylesheets

### 12.3 Animation Performance

```css
/* ✅ Hardware accelerated properties */
.animate {
  transform: translateX(100px);
  opacity: 0;
}



---

## 📝 CHECKLIST PHÁT TRIỂN

### Trước khi code:
- [ ] Xác định component cần thiết
- [ ] Check design system có component tương tự không
- [ ] Lên kế hoạch responsive behavior

### Khi viết CSS:
- [ ] Sử dụng CSS variables
- [ ] Follow BEM naming convention
- [ ] Implement dark mode support
- [ ] Test trên nhiều screen sizes


