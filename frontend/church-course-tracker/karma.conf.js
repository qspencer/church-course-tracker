// Karma configuration file, see link for more information
// https://karma-runner.github.io/1.0/config/configuration-file.html

module.exports = function (config) {
  config.set({
    basePath: '',
    frameworks: ['jasmine', '@angular-devkit/build-angular'],
    plugins: [
      require('karma-jasmine'),
      require('karma-chrome-launcher'),
      require('karma-jasmine-html-reporter'),
      require('karma-coverage'),
      require('@angular-devkit/build-angular/plugins/karma')
    ],
    client: {
      clearContext: false // leave Jasmine Spec Runner output visible in browser
    },
    jasmineHtmlReporter: {
      suppressAll: true // removes the duplicated traces
    },
    coverageReporter: {
      dir: require('path').join(__dirname, './coverage/church-course-tracker'),
      subdir: '.',
      reporters: [
        { type: 'html' },
        { type: 'text-summary' },
        { type: 'lcov' }
      ],
      check: process.env.CI ? {
        // In CI, set very low thresholds to avoid failing on coverage
        global: {
          statements: 0,
          branches: 0,
          functions: 0,
          lines: 0
        }
      } : {
        global: {
          statements: 80,
          branches: 70,
          functions: 80,
          lines: 80
        }
      }
    },
    reporters: ['progress', 'kjhtml', 'coverage'],
    port: 9876,
    colors: true,
    logLevel: config.LOG_INFO,
    autoWatch: !process.env.CI,
    browsers: process.env.CI ? ['ChromeHeadless'] : ['Chrome'],
    singleRun: !!process.env.CI,
    restartOnFileChange: !process.env.CI,
    customLaunchers: {
      ChromeHeadlessCI: {
        base: 'ChromeHeadless',
        flags: [
          '--no-sandbox',
          '--disable-gpu',
          '--disable-web-security',
          '--disable-features=VizDisplayCompositor',
          '--remote-debugging-port=9222',
          '--disable-dev-shm-usage',
          '--disable-software-rasterizer',
          '--headless=new'
        ]
      },
      ChromeHeadless: {
        base: 'Chrome',
        flags: [
          '--headless=new',
          '--no-sandbox',
          '--disable-gpu',
          '--disable-dev-shm-usage',
          '--disable-software-rasterizer'
        ]
      }
    },
    captureTimeout: 60000,
    browserNoActivityTimeout: 60000,
    browserDisconnectTimeout: 10000,
    browserDisconnectTolerance: 3
  });
};
