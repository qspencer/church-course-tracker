# DNS Configuration for quentinspencer.com

## 🌐 **Current Status**

✅ **Website is LIVE at:** http://quentinspencer.com.s3-website-us-east-1.amazonaws.com

The landing page is successfully deployed to AWS S3 and accessible via the S3 website endpoint.

## 🔧 **DNS Configuration Required**

To make `quentinspencer.com` work, you need to configure DNS records with your domain registrar.

### **Option 1: CNAME Record (Recommended)**

Add a CNAME record in your DNS settings:

```
Type: CNAME
Name: quentinspencer.com
Value: quentinspencer.com.s3-website-us-east-1.amazonaws.com
TTL: 300 (5 minutes)
```

### **Option 2: A Record (Alternative)**

If your DNS provider doesn't support CNAME for the root domain, you can use an A record:

```
Type: A
Name: quentinspencer.com
Value: [S3 Website IP Address]
TTL: 300 (5 minutes)
```

**Note:** You'll need to get the IP address from AWS or use a service like `dig` to resolve the S3 endpoint.

## 🏢 **Common DNS Providers**

### **GoDaddy**
1. Go to DNS Management
2. Add CNAME record: `@` → `quentinspencer.com.s3-website-us-east-1.amazonaws.com`
3. Save changes

### **Namecheap**
1. Go to Advanced DNS
2. Add CNAME record: `@` → `quentinspencer.com.s3-website-us-east-1.amazonaws.com`
3. Save changes

### **Cloudflare**
1. Go to DNS tab
2. Add CNAME record: `quentinspencer.com` → `quentinspencer.com.s3-website-us-east-1.amazonaws.com`
3. Set proxy status to "DNS only" (gray cloud)
4. Save changes

### **Route 53 (AWS)**
1. Go to Hosted Zones
2. Create record: `quentinspencer.com` → `quentinspencer.com.s3-website-us-east-1.amazonaws.com`
3. Set record type to CNAME
4. Save changes

## ⏱️ **DNS Propagation**

After adding the DNS record:
- **Propagation Time:** 5 minutes to 48 hours
- **Typical Time:** 15-30 minutes
- **Check Status:** Use `nslookup quentinspencer.com` or online DNS checker

## 🔍 **Testing DNS Configuration**

### **Check DNS Resolution**
```bash
nslookup quentinspencer.com
dig quentinspencer.com
```

### **Test Website Access**
```bash
curl -I http://quentinspencer.com
curl -I https://quentinspencer.com
```

### **Online DNS Checkers**
- https://dnschecker.org
- https://whatsmydns.net
- https://dns.google

## 🔒 **SSL Certificate (HTTPS)**

For HTTPS support, you'll need to set up CloudFront distribution:

### **Step 1: Create CloudFront Distribution**
```bash
# This requires AWS Console or CloudFormation
# Go to CloudFront in AWS Console
# Create distribution with S3 origin
```

### **Step 2: Configure Custom Domain**
- Add `quentinspencer.com` as alternate domain name
- Upload SSL certificate (or use AWS Certificate Manager)
- Update DNS to point to CloudFront distribution

### **Step 3: Update DNS**
```
Type: CNAME
Name: quentinspencer.com
Value: [CloudFront Distribution Domain]
TTL: 300
```

## 🚀 **Quick Setup Commands**

### **Test Current Setup**
```bash
# Test S3 website endpoint
curl -I http://quentinspencer.com.s3-website-us-east-1.amazonaws.com

# Test DNS resolution
nslookup quentinspencer.com

# Test website access
curl -I http://quentinspencer.com
```

### **Verify Deployment**
```bash
# Check S3 bucket contents
aws s3 ls s3://quentinspencer.com

# Check website configuration
aws s3api get-bucket-website --bucket quentinspencer.com
```

## 📋 **Checklist**

- [ ] ✅ S3 bucket created: `quentinspencer.com`
- [ ] ✅ Website hosting enabled
- [ ] ✅ Files uploaded to S3
- [ ] ✅ Public read access configured
- [ ] ✅ Content types set correctly
- [ ] ⏳ DNS record added (pending)
- [ ] ⏳ DNS propagation complete (pending)
- [ ] ⏳ Custom domain working (pending)
- [ ] ⏳ SSL certificate configured (optional)

## 🆘 **Troubleshooting**

### **"This site can't be reached"**
- Check DNS records are correct
- Wait for DNS propagation
- Verify domain registrar settings

### **"Site not found"**
- Check S3 bucket name matches domain
- Verify website hosting is enabled
- Check bucket policy allows public access

### **"Connection refused"**
- Check DNS resolution
- Verify S3 endpoint is correct
- Check firewall/security group settings

## 📞 **Support**

If you need help with DNS configuration:
1. Check your domain registrar's documentation
2. Contact your DNS provider's support
3. Use online DNS checkers to verify settings

## 🎉 **Next Steps**

Once DNS is configured:
1. **Test the domain:** Visit `http://quentinspencer.com`
2. **Set up HTTPS:** Configure CloudFront for SSL
3. **Monitor performance:** Set up analytics
4. **Regular updates:** Keep content fresh

The landing page is ready - just need DNS configuration! 🚀
