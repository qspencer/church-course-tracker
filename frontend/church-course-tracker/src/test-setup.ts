import 'zone.js/testing';
import { getTestBed } from '@angular/core/testing';
import {
  BrowserDynamicTestingModule,
  platformBrowserDynamicTesting
} from '@angular/platform-browser-dynamic/testing';

// First, initialize the Angular testing environment
getTestBed().initTestEnvironment(
  BrowserDynamicTestingModule,
  platformBrowserDynamicTesting(),
);

// Mock Chart.js for testing
(window as any).Chart = {
  register: () => {},
  defaults: {
    global: {
      defaultFontFamily: 'Arial'
    }
  }
};

// Mock localStorage for testing
const localStorageMock = {
  getItem: jasmine.createSpy('getItem').and.returnValue(null),
  setItem: jasmine.createSpy('setItem'),
  removeItem: jasmine.createSpy('removeItem'),
  clear: jasmine.createSpy('clear')
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

// Mock ResizeObserver for chart testing
(window as any).ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};
