# CSV Data Loading System - Complete Guide

## 🎉 **CSV Data Loading System Successfully Implemented!**

The Church Course Tracker now has a comprehensive CSV data loading system that allows you to load test data from CSV files when the application starts up.

## 🚀 **Quick Start**

### 1. Enable CSV Loading
Set these environment variables:
```bash
export LOAD_CSV_DATA=true
export CSV_DATA_DIR=data/csv
```

### 2. Create Sample Data
```bash
cd backend
python scripts/csv_data_manager.py full-setup
```

### 3. Start the Application
```bash
python main.py
```

The application will automatically load CSV data on startup!

## 📁 **What's Included**

### **CSV Files Created:**
- ✅ `campuses.csv` - 3 church campuses
- ✅ `roles.csv` - 3 user roles (admin, staff, viewer)
- ✅ `users.csv` - 4 system users
- ✅ `people.csv` - 5 church members
- ✅ `courses.csv` - 5 course offerings
- ✅ `modules.csv` - 6 course modules
- ✅ `content.csv` - 6 content items
- ✅ `enrollments.csv` - 6 course enrollments

### **Total Test Data:**
- **Users**: 1 existing + 4 from CSV
- **Roles**: 3 roles
- **Campuses**: 3 campuses
- **People**: 5 church members
- **Courses**: 5 courses
- **Modules**: 6 modules
- **Content**: 6 content items
- **Enrollments**: 6 enrollments

## 🛠 **Management Commands**

```bash
# Create sample CSV files
python scripts/csv_data_manager.py create

# Load data into database
python scripts/csv_data_manager.py load

# Force reload data (overwrites existing)
python scripts/csv_data_manager.py load --force

# Show database summary
python scripts/csv_data_manager.py summary

# Clear all database data (WARNING!)
python scripts/csv_data_manager.py clear

# Complete setup (create + load + summary)
python scripts/csv_data_manager.py full-setup
```

## ⚙️ **Configuration**

### Environment Variables:
| Variable | Default | Description |
|----------|---------|-------------|
| `LOAD_CSV_DATA` | `false` | Enable CSV data loading on startup |
| `CSV_DATA_DIR` | `data/csv` | Directory containing CSV files |
| `FORCE_RELOAD_CSV` | `false` | Force reload data even if it exists |

### Application Integration:
- ✅ **Startup Event**: CSV data loads automatically on application startup
- ✅ **Dependency Order**: Data loads in correct order (campuses → roles → users → people → courses → modules → content → enrollments)
- ✅ **Error Handling**: Graceful handling of missing files and invalid data
- ✅ **Logging**: Comprehensive logging of the loading process

## 📊 **Sample Data Overview**

### **Courses Available:**
1. **Introduction to Faith** - A foundational course on Christian faith and beliefs
2. **Bible Study Methods** - Learn how to study and interpret the Bible effectively
3. **Church History** - Explore the history of Christianity and the church
4. **Christian Ethics** - Understanding moral principles from a Christian perspective
5. **Worship and Music** - The role of music and worship in Christian life

### **User Accounts:**
- **admin** / admin123 - Administrator
- **staff** / staff123 - Church Staff
- **viewer** / viewer123 - Course Viewer
- **pastor** / pastor123 - Pastor John

### **Church Members:**
- John Doe, Jane Smith, Bob Johnson, Alice Brown, Charlie Wilson

## 🔧 **Customization**

### **Adding New Data:**
1. Edit existing CSV files in `data/csv/`
2. Add new records following the same format
3. Reload data: `python scripts/csv_data_manager.py load --force`

### **Creating New Data Types:**
1. Create new CSV file in `data/csv/`
2. Add loading logic to `app/core/csv_loader.py`
3. Update the `load_all_data()` method

## 🎯 **Use Cases**

### **Development:**
- Quick setup of test environment
- Consistent data across team members
- Easy reset and reload of test data

### **Testing:**
- Automated test data setup
- Different data scenarios
- Performance testing with realistic data

### **Demos:**
- Pre-populated database for presentations
- Realistic church data for demonstrations
- Easy setup for client demos

## 🚨 **Important Notes**

### **Data Safety:**
- CSV loading is **disabled by default** (`LOAD_CSV_DATA=false`)
- Existing data is **preserved** unless `FORCE_RELOAD_CSV=true`
- Always backup production data before enabling CSV loading

### **Performance:**
- CSV loading happens **once on startup**
- Minimal impact on application performance
- Data is loaded in memory-efficient batches

## 🎉 **Success!**

The CSV data loading system is now fully operational and ready for use. You can:

1. **Enable it** by setting `LOAD_CSV_DATA=true`
2. **Customize the data** by editing CSV files
3. **Manage the data** using the provided scripts
4. **Integrate it** into your development workflow

This system makes it easy to maintain consistent test data across different environments and team members! 🚀
