import { FullGraphZoom, GraphDataProps, LineChartDataProps, VerticalRange } from "@/lib/graphTypes";
import Ut from "./utils";



/**
 * The initial full zoom state.
 */
export const initialZoom: FullGraphZoom = {
  left: "dataMin",
  right: "dataMax",
  refAreaLeft: 0,
  refAreaRight: 0,
  topLeft: "dataMax+0.5",
  bottomLeft: "dataMin-0.5",
  topRight: "dataMax+0.5",
  bottomRight: "dataMin-0.5",
  animation: true,
};

/** Represents a single zoom configuration option */
export interface Zoom {
  /** Label for the zoom option (e.g., "5 sec") */
  label: string;
  /** Time window in seconds */
  time_window: number;
  /** Interval used in the zoom option */
  interval: number;
  /** Amount by which to move the window */
  moveBy: number;
}

/**
 * Utility class for graph-related helper functions.
 */
export class GraphHelper {
  /**
   * Provides a list of static zoom configuration options.
   * @returns An array of available zoom configurations.
   */
  static get_static_zooms(): Zoom[] {
    return [
      { label: "5 sec", time_window: 5, interval: 0, moveBy: 1 },
      { label: "10 sec", time_window: 10, interval: 0, moveBy: 1 },
      { label: "30 sec", time_window: 30, interval: 0, moveBy: 10 },
      { label: "1 min", time_window: 60, interval: 0, moveBy: 30 },
      { label: "2 min", time_window: 120, interval: 0, moveBy: 60 },
      { label: "3 min", time_window: 180, interval: 0, moveBy: 60 },
      { label: "5 min", time_window: 300, interval: 0, moveBy: 60 },
      { label: "15 min", time_window: 900, interval: 0, moveBy: 300 },
      { label: "30 min", time_window: 1800, interval: 0, moveBy: 900 },
      { label: "1 hour", time_window: 3600, interval: 10, moveBy: 1800 },
      { label: "6 hours", time_window: 21600, interval: 30, moveBy: 3600 },
      { label: "12 hours", time_window: 43200, interval: 60, moveBy: 3600 },
      { label: "1 day", time_window: 86400, interval: 120, moveBy: 3600 },
      { label: "1 week", time_window: 604800, interval: 900, moveBy: 86400 },
      { label: "2 week", time_window: 1209600, interval: 1800, moveBy: 172800 },
      { label: "1 month", time_window: 2592000, interval: 3600, moveBy: 604800 },
      { label: "1 year", time_window: 31449600, interval: 43200, moveBy: 2592000 },
      { label: "2 year", time_window: 62899200, interval: 86400, moveBy: 31449600 },
      { label: "3 year", time_window: 94348800, interval: 86400, moveBy: 31449600 },
      { label: "5 year", time_window: 157248000, interval: 604800, moveBy: 31449600 }
    ];
  }

  /**
   * Finds the zoom configuration that best matches the specified time window.
   * @param time_window - The desired time window.
   * @param default_time_window - Default time window to use when the provided time window is zero.
   * @returns The closest matching zoom configuration.
   */
  static get_zoom_by_window(
    time_window: number,
    default_time_window: number = 86400
  ): Zoom {
    const zooms = GraphHelper.get_static_zooms();
    if (time_window === 0) {
      const def = zooms.find(item => item.time_window === default_time_window);
      return def || zooms[0];
    }
    return zooms.reduce((prev, curr) =>
      Math.abs(curr.time_window - time_window) < Math.abs(prev.time_window - time_window)
        ? curr
        : prev
    );
  }

  /**
   * Retrieves the zoom configuration matching or closest to the specified time window.
   * @param time_window - The time window for which to retrieve the configuration.
   * @returns The zoom configuration that matches or is closest to the given time window.
   */
  static get_interval_by_window(time_window: number): Zoom {
    const zooms = GraphHelper.get_static_zooms();
    const exact = zooms.find(z => z.time_window === time_window);
    if (exact) {
      return exact;
    }
    // Use reduce to find the closest zoom configuration.
    const closest = zooms.reduce((prev, curr) =>
      Math.abs(curr.time_window - time_window) < Math.abs(prev.time_window - time_window)
        ? curr
        : prev
    );
    return closest || zooms[12];
  }

  /**
   * Finds the next zoom configuration that is larger than the current time window.
   * @param time_window - The current time window.
   * @returns The smallest zoom configuration that is larger than the provided time window.
   */
  static zoom_out(time_window: number): Zoom {
    const zooms = GraphHelper.get_static_zooms();
    const larger = zooms.filter(z => z.time_window > time_window);
    if (larger.length > 0) {
      return larger[0];
    }
    return zooms[zooms.length - 1];
  }

  /**
   * Finds the next zoom configuration that is smaller than the current time window.
   * @param time_window - The current time window.
   * @returns The largest zoom configuration that is smaller than the provided time window.
   */
  static zoom_in(time_window: number): Zoom {
    const zooms = GraphHelper.get_static_zooms();
    const smaller = zooms.filter(z => z.time_window < time_window);
    if (smaller.length > 0) {
      return smaller[smaller.length - 1];
    }
    return zooms[0];
  }

  /**
   * Calculates the minimum and maximum values for a given reference field within a specific time range.
   *
   * @param data - Array of data points.
   * @param from - Start of the time range.
   * @param to - End of the time range.
   * @param ref - The reference field (key) to evaluate.
   * @returns A tuple [min, max] for the reference field. Returns [null, null] if no data is found.
   */
  static getAxisYDomain(
    data: GraphDataProps[],
    from: number,
    to: number,
    ref: string
  ): [number | null, number | null] {
    const refData = data.filter(
      item => item.date !== null && item.date >= from && item.date <= to
    );
    if (refData.length === 0) {
      return [null, null];
    }
    let bottom: number | null = refData[0][ref];
    let top: number | null = refData[0][ref];

    refData.forEach(d => {
      const value = d[ref];
      if (value !== null) {
        if (top === null || value > top) {
          top = value;
        }
        if (bottom === null || value < bottom) {
          bottom = value;
        }
      }
    });
    return [bottom, top];
  }

  /**
   * Calculates the vertical range (min and max) for both left and right axes based on the data feeds.
   *
   * @param data - The complete line chart data including data points and feed configurations.
   * @param refAreaLeft - The start time (or value) of the reference area.
   * @param refAreaRight - The end time (or value) of the reference area.
   * @returns An object containing top and bottom values for both left and right axes.
   */
  static getAxisYRange(
    data: LineChartDataProps,
    refAreaLeft: number,
    refAreaRight: number
  ): {
    topLeft: number | string;
    bottomLeft: number | string;
    topRight: number | string;
    bottomRight: number | string;
  } {
    const result = {
      topLeft: initialZoom.topLeft,
      bottomLeft: initialZoom.bottomLeft,
      topRight: initialZoom.topRight,
      bottomRight: initialZoom.bottomRight,
    };

    const verticalRange: VerticalRange = data.feeds.reduce(
      (acc: VerticalRange, item) => {
        const [bottom, top] = GraphHelper.getAxisYDomain(
          data.data,
          refAreaLeft,
          refAreaRight,
          `${item.feed_id}`
        );

        if (item.location === "left") {
          if (top !== null) {
            acc.left_top.push(top);
          }
          if (bottom !== null) {
            acc.left_bottom.push(bottom);
          }
        } else {
          if (top !== null) {
            acc.right_top.push(top);
          }
          if (bottom !== null) {
            acc.right_bottom.push(bottom);
          }
        }
        return acc;
      },
      { left_top: [], left_bottom: [], right_top: [], right_bottom: [] }
    );

    if (verticalRange.left_top.length > 0 && verticalRange.left_bottom.length > 0) {
      result.topLeft = Math.max(...verticalRange.left_top);
      result.bottomLeft = Math.min(...verticalRange.left_bottom);
      const offset_left = (Number(result.topLeft) - Number(result.bottomLeft)) * 0.05;
      result.topLeft = Ut.roundFloat(Number(result.topLeft) + offset_left);
      result.bottomLeft = Ut.roundFloat(Number(result.bottomLeft) - offset_left);
    }
    if (verticalRange.right_top.length > 0 && verticalRange.right_bottom.length > 0) {
      result.topRight = Math.max(...verticalRange.right_top);
      result.bottomRight = Math.min(...verticalRange.right_bottom);
      const offset_right = (Number(result.topRight) - Number(result.bottomRight)) * 0.05;
      result.topRight = Ut.roundFloat(Number(result.topRight) + offset_right);
      result.bottomRight = Ut.roundFloat(Number(result.bottomRight) - offset_right);
    }
    return result;
  }
}