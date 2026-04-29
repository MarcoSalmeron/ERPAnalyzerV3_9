export default {  
  content: [  
    "./index.html",  
    "./src/**/*.{js,ts,jsx,tsx}",  
  ],  
  theme: {  
    extend: {  
      colors: {  
        oracle: {  
          primary: '#F80000',  
          secondary: '#312D2A',  
          dark: '#0d0f14',  
          surface: '#161b22',  
          border: '#2d3748',  
          text: '#c9d1e0',  
          muted: '#6b7280',  
          accent: '#00C2FF',  
          success: '#00D68F',  
          warning: '#FFB800',  
          error: '#FF3D3D',  
        }  
      },  
      fontFamily: {  
        sans: ['JetBrains Mono', 'Cascadia Code', 'Fira Code', 'Consolas', 'monospace'],  
        mono: ['JetBrains Mono', 'Cascadia Code', 'Fira Code', 'Consolas', 'monospace'],  
      },  
      animation: {  
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',  
        'spin-slow': 'spin 3s linear infinite',  
        'fade-in': 'fadeIn 0.3s ease-out',  
        'slide-up': 'slideUp 0.3s ease-out',  
      },  
      keyframes: {  
        'pulse-glow': {  
          '0%, 100%': { opacity: '0.4' },  
          '50%': { opacity: '1' },  
        },  
        fadeIn: {  
          '0%': { opacity: '0' },  
          '100%': { opacity: '1' },  
        },  
        slideUp: {  
          '0%': { opacity: '0', transform: 'translateY(10px)' },  
          '100%': { opacity: '1', transform: 'translateY(0)' },  
        }  
      },  
      boxShadow: {  
        'glow': '0 0 20px rgba(0, 194, 255, 0.3)',  
        'glow-strong': '0 0 30px rgba(0, 194, 255, 0.5)',  
        'glow-red': '0 0 20px rgba(248, 0, 0, 0.3)',  
      }  
    },  
  },  
  plugins: [],  
}