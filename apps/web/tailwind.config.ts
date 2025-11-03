import type { Config } from "tailwindcss"
import { fontFamily } from "tailwindcss/defaultTheme"

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#00D1FF",
          50: "#E6FBFF",
          100: "#C0F6FF",
          200: "#8AF0FF",
          300: "#54E9FF",
          400: "#1DE2FF",
          500: "#00D1FF",
          600: "#00A6CC",
          700: "#007A99",
          800: "#004F66",
          900: "#002533",
        },
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem",
      },
      boxShadow: {
        glow: "0 0 40px rgba(0,209,255,0.25)",
        "glow-lg": "0 0 60px rgba(0,209,255,0.35)",
      },
      backgroundImage: {
        "grid-neon": "linear-gradient(to right, rgba(0,209,255,.08) 1px, transparent 1px), linear-gradient(to bottom, rgba(0,209,255,.08) 1px, transparent 1px)",
      },
      fontFamily: {
        sans: ["var(--font-inter)", ...fontFamily.sans],
      },
      typography: ({ theme }: { theme: any }) => ({
        neon: {
          css: {
            "--tw-prose-body": theme("colors.slate[200]"),
            "--tw-prose-headings": theme("colors.white"),
            "--tw-prose-links": theme("colors.brand[500]"),
            "--tw-prose-bold": theme("colors.white"),
            "--tw-prose-quotes": theme("colors.slate[200]"),
            "--tw-prose-hr": "rgba(255, 255, 255, 0.1)",
            "--tw-prose-code": theme("colors.slate[200]"),
            "--tw-prose-pre-code": theme("colors.slate[200]"),
            "--tw-prose-pre-bg": "rgb(15 23 42 / 0.5)",
            "--tw-prose-th-borders": "rgba(255, 255, 255, 0.1)",
            "--tw-prose-td-borders": "rgba(255, 255, 255, 0.05)",
            a: {
              textDecoration: "underline",
              textUnderlineOffset: "3px",
              textDecorationColor: theme("colors.brand[500]"),
              transition: "all 0.2s",
              "&:hover": {
                textDecorationThickness: "2px",
              },
            },
            "h1, h2": {
              letterSpacing: "-0.02em",
              fontWeight: "600",
            },
            h1: {
              background: "linear-gradient(to right, #00D1FF, #67E8F9)",
              backgroundClip: "text",
              WebkitBackgroundClip: "text",
              color: "transparent",
            },
            h2: {
              background: "linear-gradient(to right, #00D1FF, #A5F3FC)",
              backgroundClip: "text",
              WebkitBackgroundClip: "text",
              color: "transparent",
            },
            code: {
              backgroundColor: "rgb(15 23 42 / 0.5)",
              padding: "0.2rem 0.4rem",
              borderRadius: "0.5rem",
              fontSize: "0.875em",
              fontWeight: "400",
              border: "1px solid rgba(0, 209, 255, 0.2)",
              boxShadow: "0 0 10px rgba(0, 209, 255, 0.1)",
            },
            "code::before, code::after": {
              content: '""',
            },
            pre: {
              backgroundColor: "rgb(15 23 42 / 0.5)",
              border: "1px solid rgba(0, 209, 255, 0.2)",
              borderRadius: "0.75rem",
              padding: "1rem",
              boxShadow: "0 0 20px rgba(0, 209, 255, 0.1)",
            },
            blockquote: {
              borderLeftColor: theme("colors.brand[500]"),
              borderLeftWidth: "4px",
              color: theme("colors.slate[300]"),
              paddingLeft: "1rem",
              fontStyle: "italic",
            },
            ul: {
              listStyleType: "none",
              paddingLeft: "0",
            },
            "ul li::before": {
              content: '"▸"',
              color: theme("colors.brand[500]"),
              fontWeight: "bold",
              display: "inline-block",
              width: "1em",
              marginRight: "0.5em",
            },
            hr: {
              borderColor: "rgba(255, 255, 255, 0.1)",
            },
            table: {
              borderColor: "rgba(255, 255, 255, 0.1)",
            },
            th: {
              borderColor: "rgba(255, 255, 255, 0.1)",
            },
            td: {
              borderColor: "rgba(255, 255, 255, 0.05)",
            },
          },
        },
      }),
    },
  },
  plugins: [
    require("tailwindcss-animate"),
    require("@tailwindcss/typography"),
  ],
}

export default config

