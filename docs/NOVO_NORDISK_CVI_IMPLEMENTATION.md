# Novo Nordisk Corporate Visual Identity Implementation

This document describes how the Novo Nordisk Corporate Visual Identity (CVI) guidelines have been implemented in the Clinical Trial System Reporting (CTSR) Streamlit application.

## Overview

The CTSR application now follows Novo Nordisk's CVI guidelines to ensure brand consistency and professional appearance across all user interfaces.

## Color Palette

### Primary Colors
- **True Blue** (`#001965`): Main brand color used for headings, primary text, and key UI elements
- **Snow White** (`#FFFFFF`): Background color and light UI elements

### Secondary Colors
- **Sea Blue** (`#0055B8`): Accents, links, and interactive elements
- **Light Blue** (`#7AB3E6`): Hover states and subtle highlights
- **Ocean Green** (`#4DA398`): Complementary accents
- **Rose Pink** (`#F5D1D8`): Sidebar tints and soft backgrounds

### Neutral Colors
- **Warm Grey** (`#C9C0B7`): Borders and inactive states
- **Granite Grey** (`#8B8D8F`): Fallback neutral color

### Spot Colors (Digital UI)
- **Lava Red** (`#DC143C`): Error states, failed operations, overdue items
- **Golden Yellow** (`#FFD700`): Warning states, pending items, planned activities
- **Forest Green** (`#228B22`): Success states, active items, confirmed actions

## Typography

### Font Family
- **Primary**: Arial (fallback for Novo Nordisk's Apis font)
- **Weight**: Light (300) for headings, Regular (400) for body text, Medium (500) for buttons

### Text Color
- **All text uses True Blue (`#001965`)** - Never black text per CVI guidelines
- Exception: White text on dark backgrounds for readability

### Hierarchy
- **H1**: 2.5rem, Light weight, Sea Blue bottom border
- **H2**: 1.75rem, Light weight
- **H3**: 1.25rem, Regular weight
- **Body**: Default size with True Blue color

## Layout & Spacing

### Base Unit
- **16px**: Primary spacing unit for padding, margins, and gaps
- Desktop: 16px base
- Mobile: 12-16px responsive

### Border Radius
- **4px**: Input fields, small cards
- **8px**: Metric cards, containers, dataframes
- **24px**: Pill-style buttons
- **Fully rounded**: Icon buttons, badges

### Shadows
- **Subtle elevation**: `0 2px 4px rgba(0, 25, 101, 0.05)`
- **Interactive hover**: `0 4px 8px rgba(0, 25, 101, 0.2)`

## Components

### Buttons
- **Primary Button**:
  - Background: True Blue (`#001965`)
  - Text: Snow White
  - Border radius: 24px (pill shape)
  - Padding: 10px 24px
  - Hover: Sea Blue background with shadow

- **Secondary Button**:
  - Background: Transparent
  - Border: 2px solid True Blue
  - Text: True Blue
  - Hover: Light True Blue background (5% opacity)

### Status Badges
Status badges use CVI spot colors for semantic meaning:

| Status | Color | Meaning |
|--------|-------|---------|
| ACTIVE | Forest Green | System is operational |
| CONFIRMED | Forest Green | Action completed successfully |
| VALIDATED | Forest Green | Data verified |
| HEALTHY | Forest Green | System health check passed |
| PENDING | Golden Yellow | Awaiting action |
| PLANNED | Golden Yellow | Scheduled but not started |
| OVERDUE | Lava Red | Past due date |
| FAILED | Lava Red | Operation failed |
| UNHEALTHY | Lava Red | System issue detected |
| COMPLETED | True Blue | Finished successfully |
| INACTIVE | Warm Grey | Not in use |

Badge styling:
- Border radius: 24px (pill shape)
- Padding: 6px 12px
- Font size: 0.875rem
- Font weight: 500

### Metric Cards
- Background: Snow White
- Border: 1px solid True Blue (10% opacity)
- Border radius: 8px
- Padding: 16px
- Shadow: Subtle elevation
- Label color: Sea Blue
- Value color: True Blue

### Input Fields
- Border radius: 4px
- Border: 1px Warm Grey
- Focus state: Sea Blue border with subtle shadow
- Text color: True Blue

### Tables/Dataframes
- Border radius: 8px
- Overflow: hidden for clean corners
- Headers: True Blue background
- Alternating rows: Subtle True Blue tint

### Tabs
- Active tab: True Blue background, Snow White text
- Inactive tab: Sea Blue text on white
- Border radius: 4px top corners
- Font weight: 500

### Alerts/Messages
- **Success**: Forest Green left border, light green background
- **Error**: Lava Red left border, light red background
- **Warning**: Golden Yellow left border, light yellow background
- Border radius: 4px
- Left border: 4px solid

## Sidebar
- Background: Rose Pink (15% opacity) for soft accent
- Border: True Blue (10% opacity)
- Text: True Blue
- Maintains clean separation from main content

## Links
- Default: Sea Blue
- Hover: Light Blue with underline
- No underline by default

## CVI Principles Applied

### Authentic
- Clean, professional appearance
- True to Novo Nordisk brand identity
- Consistent color usage throughout

### Simple
- Clear visual hierarchy
- Whitespace-heavy layouts
- Minimal decoration
- Focus on content

### Distinct
- Recognizable Novo Nordisk blue color scheme
- Rounded, pill-shaped buttons (characteristic NN style)
- Balanced use of spot colors for meaning
- Professional sans-serif typography

## Files Modified

1. **streamlit-app/app.py**
   - Comprehensive CVI CSS theme in `<style>` block
   - CSS variables for all NN colors
   - Typography styling (True Blue text, proper weights)
   - Component styling (buttons, cards, inputs)
   - Layout adjustments (spacing, shadows)

2. **streamlit-app/app/utils/components.py**
   - `status_badge()` function updated to use CVI spot colors
   - Pill-shaped badges (24px border radius)
   - Semantic color mapping for all statuses

## Implementation Notes

### Font Limitation
The proprietary Novo Nordisk Apis font is not available in the Streamlit environment. Arial is used as a web-safe fallback, which is acceptable per CVI guidelines.

### Logo Placement
No logo implementation yet. When added, should follow these guidelines:
- **Placement**: Top right corner
- **Clear space**: Equal to height of bull symbol
- **Minimum size**: Ensure legibility
- **Format**: Apis bull + wordmark

### Accessibility
- High contrast maintained between text and backgrounds
- True Blue on Snow White meets WCAG AA standards
- Status colors chosen for distinguishability
- Semantic HTML maintained through Streamlit components

### Responsive Behavior
Streamlit handles responsive layouts. CVI spacing adjusts through CSS:
- Desktop: 16px base spacing
- Mobile: Streamlit's responsive columns and automatic reflowing

## Testing Checklist

- [x] All colors match CVI palette
- [x] No black text (all True Blue or appropriate spot color)
- [x] Buttons are pill-shaped (24px border radius)
- [x] Metric cards use 8px border radius
- [x] Status badges use CVI spot colors
- [x] Typography uses True Blue for headers
- [x] Spacing uses 16px base unit
- [x] Input fields have 4px border radius
- [x] Shadows use subtle True Blue tints
- [x] Links use Sea Blue → Light Blue on hover
- [x] Sidebar has Rose Pink tint
- [x] Success/error/warning use spot colors

## Future Enhancements

1. **Logo Integration**: Add Novo Nordisk Apis bull + wordmark logo in top-right placement
2. **Custom Font**: If Apis font becomes available for web use, load via CSS @font-face
3. **Animations**: Consider adding subtle transitions following CVI motion principles
4. **Dark Mode**: Potential dark theme variant using CVI colors (if requested)
5. **Print Styles**: CSS for print media using CVI guidelines for documentation

## References

- **Source**: `novo-nordisk-cvi-guidelines.md` (workspace documentation)
- **CVI Version**: Novo Nordisk Corporate Visual Identity Guidelines
- **Implementation Date**: 2024
- **Last Updated**: 2024

## Compliance Statement

This implementation follows Novo Nordisk Corporate Visual Identity guidelines for digital applications. All color values, typography rules, spacing standards, and component styles align with official CVI specifications for brand consistency.
