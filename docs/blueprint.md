# **App Name**: Paper Brain

## Core Features:

- Invoice Generation Online: Allows users to fill out an invoice form with fields corresponding to the invoice template.
- Live Preview: Dynamically update the invoice template preview as the user edits the form fields.
- PDF Download: Generates and downloads a pixel-perfect A4 PDF of the invoice using the current form data and template.
- Template Rendering: Render an HTML/CSS invoice template in react, so the display matches the PDF output.
- Form State Autosave: Save form state to local storage every 5 seconds.
- Amount in Words Converter: Use generative AI to generate the invoice's total amount in words. It should intelligently choose when to represent the numbers as words, versus leaving them as numerical.
- Invoice Generation from Photo (Placeholder): Displays a disabled button with a tooltip indicating 'Coming Soon,' providing a placeholder for future functionality.

## Style Guidelines:

- Primary color: Light grayish blue (#D1D5DB) for a professional, neutral tone.
- Background color: White (#FFFFFF) for a clean and crisp appearance.
- Accent color: Soft Blue (#9CA3AF) to add visual interest without overwhelming the user.
- Font: 'Inter' (sans-serif) for both headlines and body text to ensure readability and a modern aesthetic.
- Font for code: 'Source Code Pro' (monospace).
- Maintain a clean and organized layout, dividing the screen into a left column for the form and a right column for the live preview.
- Subtle transitions when updating the live preview for a smooth user experience.