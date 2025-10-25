# Landing Page Deployment Guide

This guide covers different ways to deploy the Quentin Spencer landing page to quentinspencer.com.

## Quick Start

The landing page is ready to deploy with the following files:
- `index.html` - Main page
- `styles.css` - Styling and animations
- `script.js` - Interactive functionality
- `favicon.svg` - Site icon
- `robots.txt` - Search engine instructions
- `sitemap.xml` - Site structure for search engines

## Deployment Options

### Option 1: AWS S3 + CloudFront (Recommended)

1. **Create S3 Bucket:**
   ```bash
   aws s3 mb s3://quentinspencer.com
   ```

2. **Configure for Static Website Hosting:**
   ```bash
   aws s3 website s3://quentinspencer.com --index-document index.html --error-document index.html
   ```

3. **Deploy Files:**
   ```bash
   export S3_BUCKET=quentinspencer.com
   ./deploy.sh s3
   ```

4. **Set up CloudFront Distribution:**
   - Create CloudFront distribution
   - Point to S3 bucket
   - Configure custom domain (quentinspencer.com)
   - Set up SSL certificate

### Option 2: Netlify

1. **Install Netlify CLI:**
   ```bash
   npm install -g netlify-cli
   ```

2. **Deploy:**
   ```bash
   ./deploy.sh netlify
   ```

3. **Configure Custom Domain:**
   - Add quentinspencer.com in Netlify dashboard
   - Update DNS records

### Option 3: Vercel

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Deploy:**
   ```bash
   vercel --prod
   ```

3. **Configure Custom Domain:**
   - Add quentinspencer.com in Vercel dashboard
   - Update DNS records

### Option 4: GitHub Pages

1. **Create GitHub Repository:**
   - Create new repository
   - Upload files

2. **Enable GitHub Pages:**
   - Go to repository settings
   - Enable Pages from main branch
   - Set custom domain to quentinspencer.com

3. **Update DNS:**
   - Point quentinspencer.com to GitHub Pages

### Option 5: Traditional Web Server

1. **Upload Files:**
   - Upload all files to web server root
   - Ensure index.html is in the root directory

2. **Configure Web Server:**
   - Apache: Enable mod_rewrite for clean URLs
   - Nginx: Configure proper MIME types
   - IIS: Set up default document

## DNS Configuration

### For quentinspencer.com

1. **A Record:**
   ```
   quentinspencer.com -> [Server IP or CNAME target]
   ```

2. **CNAME Record (if using CDN):**
   ```
   quentinspencer.com -> [CDN domain]
   ```

3. **WWW Redirect:**
   ```
   www.quentinspencer.com -> quentinspencer.com
   ```

## SSL Certificate

### Let's Encrypt (Free)
```bash
certbot --nginx -d quentinspencer.com -d www.quentinspencer.com
```

### AWS Certificate Manager
- Request certificate for quentinspencer.com
- Validate domain ownership
- Attach to CloudFront distribution

### Cloudflare
- Add domain to Cloudflare
- Enable SSL/TLS encryption
- Set to "Full (strict)" mode

## Performance Optimization

### 1. Enable Compression
```nginx
# Nginx
gzip on;
gzip_types text/css application/javascript text/html;
```

### 2. Set Cache Headers
```nginx
# Nginx
location ~* \.(css|js|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. Use CDN
- CloudFlare (free tier available)
- AWS CloudFront
- MaxCDN

## Monitoring

### 1. Analytics
- Google Analytics
- Google Search Console
- Bing Webmaster Tools

### 2. Uptime Monitoring
- UptimeRobot (free)
- Pingdom
- StatusCake

### 3. Performance Monitoring
- Google PageSpeed Insights
- GTmetrix
- WebPageTest

## Security

### 1. HTTPS Only
- Redirect HTTP to HTTPS
- Use HSTS headers

### 2. Security Headers
```nginx
# Nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
```

### 3. Content Security Policy
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; script-src 'self' 'unsafe-inline';">
```

## Backup Strategy

### 1. Version Control
- Keep files in Git repository
- Tag releases for easy rollback

### 2. File Backup
- Regular backups of web server files
- Store backups in multiple locations

### 3. DNS Backup
- Document DNS configuration
- Keep backup of DNS records

## Troubleshooting

### Common Issues

1. **Files Not Loading:**
   - Check file permissions (644 for files, 755 for directories)
   - Verify MIME types are correct
   - Check for typos in file names

2. **CSS/JS Not Working:**
   - Check file paths are correct
   - Verify files are uploaded completely
   - Check browser console for errors

3. **SSL Issues:**
   - Verify certificate is valid
   - Check certificate chain
   - Ensure proper redirect from HTTP to HTTPS

4. **DNS Issues:**
   - Verify DNS propagation
   - Check TTL values
   - Test with different DNS servers

### Testing Checklist

- [ ] Site loads on quentinspencer.com
- [ ] HTTPS redirect works
- [ ] All links work correctly
- [ ] Mobile responsive design
- [ ] Fast loading times
- [ ] No console errors
- [ ] SEO meta tags present
- [ ] Favicon displays correctly

## Maintenance

### Regular Tasks
- Monitor site uptime
- Check for broken links
- Update content as needed
- Review analytics data
- Keep dependencies updated

### Monthly Tasks
- Review performance metrics
- Check security headers
- Update sitemap if needed
- Backup configuration files

## Support

For deployment issues:
- Check hosting provider documentation
- Review server logs
- Test with different browsers
- Use browser developer tools

## Cost Estimation

### Free Options
- GitHub Pages (free)
- Netlify (free tier)
- Vercel (free tier)

### Low Cost Options
- AWS S3 + CloudFront (~$1-5/month)
- Shared hosting (~$3-10/month)
- VPS (~$5-20/month)

### Premium Options
- Dedicated server (~$50-200/month)
- Managed hosting (~$20-100/month)
