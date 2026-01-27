# AI Learning Platform - Frontend

Nền tảng học tập AI thông minh với React + JavaScript + CSS

## 🚀 Tính năng chính

- 🎓 **Quản lý khóa học**: Tạo, chỉnh sửa và theo dõi khóa học
- 👥 **Hệ thống người dùng**: Admin, Instructor, Student với quyền hạn phân cấp
- 📊 **Dashboard thống kê**: Theo dõi tiến độ và hiệu suất học tập
- 💬 **Chat hỗ trợ**: Tương tác trực tiếp với instructor
- 📝 **Quiz & Bài tập**: Hệ thống đánh giá tự động
- 🏆 **Bảng xếp hạng**: Tạo động lực học tập
- 🌙 **Dark/Light mode**: Giao diện thân thiện
- 🌐 **Đa ngôn ngữ**: Hỗ trợ Tiếng Việt và English

## 🛠️ Công nghệ sử dụng

- **Frontend Framework**: React 18.2.0
- **Build Tool**: Vite 7.1.6
- **Styling**: CSS với CSS Variables
- **State Management**: Zustand 4.5.4
- **Routing**: React Router DOM 6.26.1
- **HTTP Client**: Axios 1.4.0
- **Form Handling**: React Hook Form 7.62.0
- **Animations**: Framer Motion 11.12.0
- **Notifications**: React Hot Toast 2.4.1

## 📋 Yêu cầu hệ thống

- Node.js 18.0.0+
- npm 8.0.0+ hoặc yarn 1.22.0+
- Git

## 🏃‍♂️ Cài đặt và chạy

### 1. Clone repository
```bash
git clone <repository-url>
cd learning-app-fe/FE
```

### 2. Cài đặt dependencies
```bash
npm install
# hoặc
yarn install
```

### 3. Cấu hình environment
```bash
# Copy file cấu hình mẫu
cp .env.example .env

# Chỉnh sửa file .env theo môi trường của bạn
# Ít nhất cần cấu hình VITE_API_BASE_URL
```

### 4. Chạy development server
```bash
npm run dev
# hoặc
yarn dev
```

Ứng dụng sẽ chạy tại http://localhost:5173

### 5. Build cho production
```bash
npm run build
# hoặc
yarn build
```

## 📁 Cấu trúc thư mục

```
FE/
├── public/                 # Static assets
├── src/
│   ├── components/        # React components
│   │   ├── ui/           # UI components (Button, Card, Input...)
│   │   └── layout/       # Layout components
│   ├── pages/            # Page components
│   │   ├── auth/         # Authentication pages
│   │   ├── admin/        # Admin pages
│   │   ├── courses/      # Course pages
│   │   └── ...
│   ├── services/         # API services
│   ├── stores/           # Zustand stores
│   ├── contexts/         # React contexts
│   ├── styles/           # CSS files
│   └── types/            # Type definitions
├── vite.config.js        # Vite configuration
└── package.json          # Dependencies
```

## 🎨 Hệ thống Design

### CSS Variables
Sử dụng CSS Variables cho colors, spacing, typography:
```css
:root {
  --primary: 59 130 246;     /* Blue-500 */
  --secondary: 99 102 241;   /* Indigo-500 */
  --success: 34 197 94;      /* Green-500 */
  --warning: 245 158 11;     /* Amber-500 */
  --error: 239 68 68;        /* Red-500 */
}
```

### Responsive Design
- Mobile-first approach
- Breakpoints: sm(640px), md(768px), lg(1024px), xl(1280px)
- CSS Grid và Flexbox

### Dark Mode
- Automatic system preference detection
- Manual toggle với persistence
- CSS Variables cho theme switching

## 🔐 Authentication

### User Roles
- **Admin**: Quản lý toàn bộ hệ thống
- **Instructor**: Tạo và quản lý khóa học
- **Student**: Tham gia khóa học và làm bài tập

### Protected Routes
```javascript
<ProtectedRoute allowedRoles={['admin']}>
  <AdminPage />
</ProtectedRoute>
```

## 📊 State Management

### Zustand Stores
- `authStore`: Authentication state
- `courseStore`: Course data
- `enrollmentStore`: Enrollment management
- `quizStore`: Quiz and assessment data

### Usage
```javascript
import { useAuthStore } from '../stores/authStore';

const { user, login, logout } = useAuthStore();
```

## 🌐 API Integration

### Base Configuration
```javascript
// services/api.js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
```

### Service Pattern
```javascript
// services/courseService.js
export const courseService = {
  getCourses: () => api.get('/courses'),
  getCourse: (id) => api.get(`/courses/${id}`),
  createCourse: (data) => api.post('/courses', data),
};
```

## 🧪 Testing

```bash
# Chạy tests
npm test

# Test coverage
npm run test:coverage
```

## 📦 Build và Deploy

### Development Build
```bash
npm run build:dev
```

### Production Build
```bash
npm run build
npm run preview  # Preview production build
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 5173
CMD ["npm", "run", "preview"]
```

## 🔧 Scripts có sẵn

```bash
npm run dev          # Development server
npm run build        # Production build
npm run preview      # Preview production build
npm run lint         # Lint code
npm run lint:fix     # Fix linting issues
npm run format       # Format code với Prettier
```

## 📝 Coding Standards

### JavaScript
- ES6+ features
- Functional programming approach
- JSDoc comments cho functions
- Consistent naming conventions

### CSS
- BEM naming convention
- CSS Variables
- Mobile-first responsive
- Consistent spacing scale

### React
- Functional components với Hooks
- Custom hooks cho logic tái sử dụng
- Proper prop validation
- Component composition

## 🚀 Performance

### Optimization
- Code splitting với React.lazy()
- Image optimization
- CSS purging
- Bundle analysis

### Best Practices
- Lazy loading components
- Debounced search
- Optimized re-renders
- Efficient state management

