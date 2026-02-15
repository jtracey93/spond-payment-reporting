# Spond Payment Reporting Web App - Visual Overview

## 🎨 User Interface Preview

The web app features a modern, clean interface with the following sections:

### 1. Header Section
```
┌─────────────────────────────────────────────────────────┐
│        Spond Payment Reporting                          │
│   View and analyze payment data from your Spond club    │
└─────────────────────────────────────────────────────────┘
```

### 2. Authentication Section
```
┌─────────────────────────────────────────────────────────┐
│ Authentication                                          │
│                                                         │
│ To use this app, you need a bearer token from Spond.   │
│ [How to get a bearer token?]                           │
│                                                         │
│ Bearer Token:                                           │
│ [●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●] [Show]          │
│                                                         │
│ Club ID:                                                │
│ [Enter club ID or fetch from available clubs]          │
│ [Fetch Clubs]                                           │
│                                                         │
│ [Load Payment Data]                                     │
└─────────────────────────────────────────────────────────┘
```

### 3. Filters & Sorting Section (shown after data loads)
```
┌─────────────────────────────────────────────────────────┐
│ Filters & Sorting                                       │
│                                                         │
│ Search: [____________________]                          │
│                                                         │
│ Sort By: [Member Name (A-Z) ▼]                        │
│                                                         │
│ View: [Granular Details ▼]                            │
│                                                         │
│ [Export as CSV] [Export as Excel] [Export as PDF]      │
└─────────────────────────────────────────────────────────┘
```

### 4. Data Table Section
```
┌─────────────────────────────────────────────────────────┐
│ Payment Data                                            │
│                                                         │
│ Total Items: 44 | Filtered: 44 | Total: £1,234.56     │
│ Members: 52 | Payments: 12                             │
│                                                         │
│ ┌────────────┬──────────────┬─────────────┬──────────┐ │
│ │ Member     │ Payment      │ Amount Owed │ Currency │ │
│ │ Name       │ Name         │             │          │ │
│ ├────────────┼──────────────┼─────────────┼──────────┤ │
│ │ John Smith │ Match Fee    │ 25.00       │ GBP      │ │
│ │ Jane Doe   │ Match Fee    │ 25.00       │ GBP      │ │
│ │ Bob Wilson │ Membership   │ 100.00      │ GBP      │ │
│ │ ...        │ ...          │ ...         │ ...      │ │
│ └────────────┴──────────────┴─────────────┴──────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 5. Footer
```
┌─────────────────────────────────────────────────────────┐
│ Spond Payment Reporting Tool | GitHub | Not affiliated │
│                    with Spond                           │
└─────────────────────────────────────────────────────────┘
```

## 🎯 Key Features

### Color Scheme
- **Primary Color**: Blue (#2563eb) - Used for buttons, links, and headings
- **Background**: Light gray (#f8fafc) - Clean, easy on the eyes
- **Cards**: White with subtle shadows for depth
- **Text**: Dark gray (#1e293b) for primary text
- **Secondary Text**: Medium gray (#64748b) for less important info

### Responsive Design
- **Desktop**: Full-width layout with side-by-side filters
- **Tablet**: Adapts to narrower screens with stacked layouts
- **Mobile**: Single-column layout with touch-friendly buttons

### Interactive Elements
- **Hover Effects**: Buttons and table rows change color on hover
- **Loading Spinner**: Animated spinner during data loading
- **Status Messages**: Color-coded (green for success, red for errors)
- **Club Selection**: Clickable cards for choosing clubs

### Export Formats

#### CSV Export
- Comma-separated values
- Opens in Excel, Google Sheets, or any spreadsheet software
- Includes current filters

#### Excel Export
- Tab-separated format (.xls)
- Native Excel compatibility
- Preserves formatting

#### PDF Export
- Uses browser's print dialog
- Print-optimized styles:
  - Removes buttons and filters
  - Keeps only essential data
  - Black borders on tables
  - Alternate row shading for readability
  - Page break handling

## 📱 Mobile Experience

On mobile devices:
- Touch-friendly buttons (minimum 44px tap targets)
- Scrollable tables with horizontal overflow
- Stacked form fields for easier input
- Simplified navigation
- Same functionality as desktop

## 🔒 Security & Privacy

- **No Server**: All processing happens in browser
- **No Storage**: Token and data never saved
- **Direct API**: Calls go straight to Spond
- **Client-Side Only**: No backend or database
- **Open Source**: Code is fully auditable

## 🌐 Browser Support

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Opera 76+

## 📊 Data Views

### Granular Details View
Shows every individual unpaid payment:
- Member Name
- Payment Name
- Amount Owed
- Currency

### Summary by Member View
Shows totals per member:
- Member Name
- Total Amount Owed
- Currency
- Number of Payments

## 🎨 Design Principles

1. **Simplicity**: Clean, uncluttered interface
2. **Clarity**: Clear labels and instructions
3. **Consistency**: Uniform styling throughout
4. **Accessibility**: Good contrast ratios and readable fonts
5. **Responsiveness**: Works on any device
6. **Performance**: Fast loading and smooth interactions

## 🚀 User Flow

1. User opens the web app
2. User enters bearer token (or clicks link to learn how to get one)
3. User either:
   - Enters club ID directly, OR
   - Clicks "Fetch Clubs" to see available clubs
4. User clicks "Load Payment Data"
5. App fetches members and payments from Spond API
6. Data is processed and displayed in a table
7. User can:
   - Search/filter the data
   - Sort by different columns
   - Switch between granular and summary views
   - Export to CSV, Excel, or PDF

## ✨ Additional Features

- **Token Visibility Toggle**: Show/hide token for security
- **Instructions Panel**: Collapsible help text
- **Real-time Stats**: Updates as you filter
- **Error Handling**: Helpful error messages
- **Loading States**: Visual feedback during API calls
