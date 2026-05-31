# StoryMood Frontend 🌟

A beautiful, world-class React application for AI-powered story generation with stunning visual design, smooth animations, and an intuitive user experience.

## ✨ Features

- **Beautiful UI/UX**: World-class design with gradients, animations, and responsive layout
- **Mood-Based Stories**: Generate stories based on different emotional tones
- **Multiple Story Types**: Adventure, Fantasy, Moral, Comedy, Mystery, Sci-Fi, and more
- **Custom Characters**: Add your own characters with names, ages, and traits
- **Multiple Narrator Styles**: Choose from various voice styles for story narration
- **Multi-language Support**: English, Hindi, Telugu, Tamil, Malayalam
- **Real-time Generation**: Smooth loading states and error handling
- **Responsive Design**: Perfect on desktop, tablet, and mobile devices
- **Accessibility**: Full keyboard navigation and screen reader support

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm
- Your StoryMood backend running on `http://localhost:8000`

### Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Open your browser:**
   Visit `http://localhost:3000` to see your beautiful StoryMood application!

### Environment Configuration

Create a `.env` file in the frontend directory:

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000

# Optional: Enable development features
REACT_APP_ENV=development
```

## 🎨 Design Features

### Visual Design
- **Gradient Backgrounds**: Beautiful multi-color gradients throughout the app
- **Glassmorphism**: Modern frosted glass effects with backdrop blur
- **Smooth Animations**: Delightful micro-interactions and transitions
- **Typography**: Inter font family for perfect readability
- **Color Psychology**: Mood-specific color schemes for different story types

### User Experience
- **Progressive Disclosure**: Advanced options are hidden until needed
- **Visual Feedback**: Loading states, hover effects, and success animations
- **Error Handling**: Friendly error messages with retry options
- **Responsive Grid**: Perfect layout on all screen sizes
- **Accessibility**: WCAG 2.1 AA compliant

## 🛠️ Available Scripts

```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Lint code
npm run lint

# Fix linting issues
npm run lint:fix
```

## 📱 Responsive Breakpoints

- **Mobile**: < 480px
- **Tablet**: 480px - 768px
- **Desktop**: > 768px

## 🎭 Component Structure

```
src/
├── components/
│   ├── StoryGenerator.tsx    # Main story generation form
│   └── StoryGenerator.css    # World-class styling
├── services/
│   └── apiService.ts         # API communication layer
├── types/
│   └── api.ts               # TypeScript interfaces
├── App.tsx                  # Main application component
├── App.css                  # Global app styles
├── index.tsx               # Application entry point
└── index.css               # Global styles and fonts
```

## 🔧 Configuration

### API Integration

The frontend automatically connects to your backend API. Make sure your backend is running and accessible at the configured URL.

### Backend Requirements

Your backend should provide:
- `POST /generate-story` - Story generation endpoint
- Proper CORS configuration for frontend domain
- Error responses in the format: `{ "detail": "Error message" }`

## 🌈 Color Palette

```css
/* Primary Gradients */
--primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
--success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);

/* Mood Colors */
--soothing: linear-gradient(135deg, #A8E6CF 0%, #7FCDCD 100%);
--joyful: linear-gradient(135deg, #FFD93D 0%, #FF6B6B 100%);
--magical: linear-gradient(135deg, #DDA0DD 0%, #9370DB 100%);
--intense: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
```

## 🎯 Performance Optimizations

- **Code Splitting**: Automatic code splitting with React.lazy()
- **Image Optimization**: WebP format with fallbacks
- **CSS Optimization**: Minified and tree-shaken in production
- **Font Loading**: Optimized Google Fonts loading
- **Bundle Analysis**: Built-in bundle analyzer

## 🔍 Browser Support

- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` directory.

### Deploy to Netlify

1. Connect your GitHub repository to Netlify
2. Set build command: `npm run build`
3. Set publish directory: `build`
4. Add environment variables in Netlify dashboard

### Deploy to Vercel

```bash
npx vercel --prod
```

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check if backend is running on correct port
   - Verify CORS configuration
   - Check environment variables

2. **Build Errors**
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Clear cache: `npm start -- --reset-cache`

3. **TypeScript Errors**
   - Update dependencies: `npm update`
   - Check tsconfig.json configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- **Design Inspiration**: Modern UI/UX principles and glassmorphism trends
- **Color Palettes**: Carefully selected for emotional impact
- **Typography**: Inter font for optimal readability
- **Icons**: Emoji for universal understanding and delight