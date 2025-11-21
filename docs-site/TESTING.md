# Testing the Documentation Site Locally

## 🚀 Quick Start

The documentation site is now running locally! You can access it at:

**http://127.0.0.1:8000**

## 📋 What to Test

### 1. Navigation
- [ ] Click through all main navigation items (Home, Getting Started, User Guide, Features)
- [ ] Test the sidebar navigation
- [ ] Verify table of contents works on each page
- [ ] Check that "Back to top" button appears when scrolling
- [ ] Test previous/next navigation in footer

### 2. Search Functionality
- [ ] Click the search icon in the header
- [ ] Try searching for keywords like "course", "enrollment", "progress"
- [ ] Verify search results are relevant
- [ ] Check that search highlights terms in results

### 3. Responsive Design
- [ ] Resize browser window to test mobile view
- [ ] Check that hamburger menu works on mobile
- [ ] Verify content is readable on small screens
- [ ] Test on different browser sizes (mobile, tablet, desktop)

### 4. Content Review
- [ ] Read through each page to check for typos
- [ ] Verify all links work correctly
- [ ] Check that callout boxes (tips, warnings, info) display properly
- [ ] Ensure formatting looks good

### 5. Features
- [ ] Test dark mode toggle (if available)
- [ ] Verify footer links work (Main Application, API Docs, GitHub)
- [ ] Check that external links open in new tabs
- [ ] Test print preview (File > Print)

### 6. Performance
- [ ] Check page load times
- [ ] Verify images load quickly
- [ ] Test navigation speed

### 7. Accessibility
- [ ] Test keyboard navigation (Tab key)
- [ ] Check that skip links work
- [ ] Verify screen reader compatibility (if available)
- [ ] Test color contrast

## 🛑 Stopping the Server

To stop the local server, press `Ctrl+C` in the terminal where it's running.

## 🔄 Restarting the Server

If you need to restart:

```bash
cd docs-site
source venv/bin/activate
mkdocs serve --dev-addr=127.0.0.1:8000
```

## 📝 Making Changes

While the server is running:
1. Edit any Markdown file in `docs-site/docs/`
2. The page will automatically reload in your browser
3. Changes appear immediately (hot reload)

## 🐛 Troubleshooting

**Port already in use?**
- Try a different port: `mkdocs serve --dev-addr=127.0.0.1:8001`

**Changes not showing?**
- Hard refresh your browser (Ctrl+F5 or Cmd+Shift+R)
- Check the terminal for error messages

**Build errors?**
- Run `mkdocs build` to see detailed error messages
- Check that all Markdown files are valid

## ✅ Ready for Deployment?

Once you've tested everything and are satisfied:
- All navigation works correctly
- Search functions properly
- Content looks good
- No broken links
- Responsive design works

Then we can proceed to Phase 5: Deployment!


