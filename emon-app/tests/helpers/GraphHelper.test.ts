// src/GraphHelper.test.ts
import { describe, test, expect } from 'vitest';
import { GraphHelper, initialZoom } from '../../src/helpers/graphHelper';
import type { GraphDataProps, LineChartDataProps } from '../../src/lib/graphTypes';

// --- Mocks / Helpers ---
// If Ut.isNumber is used, you can mock it here (if needed)
// For these tests we assume Ut.isNumber simply returns true for numbers.
import Ut from '../../src/helpers/utils';
Ut.isNumber = (value: unknown): value is number => typeof value === 'number';

// Helper: create sample data for getAxisYDomain and getAxisYRange
const sampleData: GraphDataProps[] = [
  { date: 100, '1': 10, '2': 20 },
  { date: 150, '1': 15, '2': 25 },
  { date: 200, '1': 5,  '2': null },
  { date: 250, '1': 20, '2': 30 },
];

const sampleChartData: LineChartDataProps = {
  data: sampleData,
  feeds: [
    { feed_id: 1, location: 'left' },
    { feed_id: 2, location: 'right' },
  ],
};

describe('GraphHelper', () => {
  // --- Time Utilities ---
  
  // --- Zoom and Interval Selection ---
  describe('Zoom and Interval Selection', () => {
    test('get_static_zooms returns a non-empty array', () => {
      const zooms = GraphHelper.get_static_zooms();
      expect(zooms.length).toBeGreaterThan(0);
    });

    test('get_zoom_by_window returns the default zoom when time_window is 0', () => {
      const defaultZoom = GraphHelper.get_zoom_by_window(0, 86400);
      // Default should be the one with time_window of 86400 (1 day)
      expect(defaultZoom.time_window).toBe(86400);
    });

    test('get_zoom_by_window returns the closest matching zoom configuration', () => {
      // Exact match:
      const zoomExact = GraphHelper.get_zoom_by_window(10);
      expect(zoomExact.time_window).toBe(10);

      // No exact match; 7 is closer to 5 than to 10 (abs diff: 2 vs 3)
      const zoomClosest = GraphHelper.get_zoom_by_window(7);
      expect(zoomClosest.time_window).toBe(5);
    });

    test('get_interval_by_window returns the zoom config for an exact match', () => {
      const intervalZoom = GraphHelper.get_interval_by_window(60);
      expect(intervalZoom.time_window).toBe(60);
    });

    test('get_interval_by_window returns the closest configuration when no exact match', () => {
      // If we pass a time_window that doesn’t exactly match, it should return the closest
      const zoomClosest = GraphHelper.get_interval_by_window(8);
      // 8 is closer to 10 than to 5? (abs diff: 2 vs 3) so expected time_window is 10
      expect(zoomClosest.time_window).toBe(10);
    });

    test('zoom_out returns the smallest zoom configuration larger than the current window', () => {
      // For a time window of 5, the next larger option is 10 sec.
      const zoomOut = GraphHelper.zoom_out(5);
      expect(zoomOut.time_window).toBeGreaterThan(5);
      // For an extremely large time window, should return the last element.
      const zoomOutMax = GraphHelper.zoom_out(200000000);
      const staticZooms = GraphHelper.get_static_zooms();
      expect(zoomOutMax).toEqual(staticZooms[staticZooms.length - 1]);
    });

    test('zoom_in returns the largest zoom configuration smaller than the current window', () => {
      // For a time window of 10, the largest option smaller than 10 is 5.
      const zoomIn = GraphHelper.zoom_in(10);
      expect(zoomIn.time_window).toBeLessThan(10);
      // For an extremely small time window, should return the first element.
      const zoomInMin = GraphHelper.zoom_in(1);
      const staticZooms = GraphHelper.get_static_zooms();
      expect(zoomInMin).toEqual(staticZooms[0]);
    });
  });

  // --- Axis Domain and Range ---
  describe('Axis Domain and Range', () => {
    test('getAxisYDomain returns [null, null] when no data in range', () => {
      const [min, max] = GraphHelper.getAxisYDomain(sampleData, 300, 400, '1');
      expect(min).toBeNull();
      expect(max).toBeNull();
    });

    test('getAxisYDomain computes correct min and max for valid data', () => {
      const [min, max] = GraphHelper.getAxisYDomain(sampleData, 100, 250, '1');
      expect(min).toBe(5);
      expect(max).toBe(20);
    });

    test('getAxisYRange computes vertical range for left and right axes with offsets', () => {
      const axisRange = GraphHelper.getAxisYRange(sampleChartData, 100, 250);

      // Check that the result has all four keys and that they are numbers
      expect(typeof axisRange.topLeft).toBe('number');
      expect(typeof axisRange.bottomLeft).toBe('number');
      expect(typeof axisRange.topRight).toBe('number');
      expect(typeof axisRange.bottomRight).toBe('number');

      // For feed '1' (left): values are [10, 15, 5, 20]
      // The raw min is 5, max is 20. With a 5% offset, expect:
      // offset = (20 - 5) * 0.05 = 0.75, so topLeft should be approximately 20.75 and bottomLeft approximately 4.25.
      expect(axisRange.topLeft).toBeCloseTo(20.75, 2);
      expect(axisRange.bottomLeft).toBeCloseTo(4.25, 2);

      // For feed '2' (right): values are [20, 25, 30] (ignoring the null)
      // Raw min is 20, max is 30; offset = (30 - 20) * 0.05 = 0.5, so topRight ≈ 30.5 and bottomRight ≈ 19.5.
      expect(axisRange.topRight).toBeCloseTo(30.5, 2);
      expect(axisRange.bottomRight).toBeCloseTo(19.5, 2);
    });
  });
});