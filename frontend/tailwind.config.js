/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--sapBackgroundColor)',
        foreground: 'var(--sapTextColor)',
        card: {
          DEFAULT: 'var(--sapGroup_ContentBackground)',
          foreground: 'var(--sapTextColor)',
        },
        popover: {
          DEFAULT: 'var(--sapTile_Background)',
          foreground: 'var(--sapTextColor)',
        },
        primary: {
          DEFAULT: 'var(--sapButton_Emphasized_Background)',
          foreground: 'var(--sapButton_Emphasized_TextColor)',
        },
        secondary: {
          DEFAULT: 'var(--sapButton_Background)',
          foreground: 'var(--sapButton_TextColor)',
        },
        muted: {
          DEFAULT: 'var(--sapNeutralBackground)',
          foreground: 'var(--sapContent_LabelColor)',
        },
        accent: {
          DEFAULT: 'var(--sapNeutralBackground)',
          foreground: 'var(--sapTextColor)',
        },
        destructive: {
          DEFAULT: 'var(--sapButton_Reject_Background)',
          foreground: 'var(--sapButton_Reject_TextColor)',
        },
        border: 'var(--sapList_BorderColor)',
        input: 'var(--sapField_BorderColor)',
        ring: 'var(--sapButton_Emphasized_Background)',
        status: {
          disponible: {
            DEFAULT: 'var(--sapSuccessBackground)',
            foreground: 'var(--sapPositiveTextColor)',
            border: 'var(--sapSuccessBorderColor)',
          },
          'en-uso': {
            DEFAULT: 'var(--sapInformationBackground)',
            foreground: 'var(--sapInformationTextColor)',
            border: 'var(--sapInformationBorderColor)',
          },
          malograda: {
            DEFAULT: 'var(--sapErrorBackground)',
            foreground: 'var(--sapNegativeTextColor)',
            border: 'var(--sapErrorBorderColor)',
          },
          perdida: {
            DEFAULT: 'var(--sapNeutralBackground)',
            foreground: 'var(--sapNeutralTextColor)',
            border: 'var(--sapNeutralBorderColor)',
          },
        },
      },
      borderRadius: {
        none: '0',
        sm: '0.125rem',
        DEFAULT: '0.125rem',
        md: '0.125rem',
        lg: '0.125rem',
        xl: '0.125rem',
        '2xl': '0.125rem',
        '3xl': '0.125rem',
        full: '0.125rem',
      },
      fontFamily: {
        sans: ['"72"', '"72full"', 'sans-serif'],
        mono: ['"72 Mono"', '"Fira Code"', '"IBM Plex Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
