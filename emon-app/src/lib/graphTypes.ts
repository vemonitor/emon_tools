
  /**
   * Represents a single data point for the graph.
   * Requires a numeric `date` property and allows additional key-value pairs.
   */
  export type SelectedFeedsProps = {file_name: string, position: GraphLocationProps}

  export type FeedMetaOut = {
    start_time: number,
    end_time: number,
    npoints: number,
    interval: number
  }

  export type FeedMetaResponse = {
    success: boolean,
    feed_id: number,
    data: FeedMetaOut[]
  }

  export type DataViewerProps = {
    source: FinaSourceProps
  }
  
  export interface GraphDataProps {
    date: number;
    [key: string]: number | null;
  }

  export type FinaSourceProps = "emoncms" | "archive"
  
  /** Allowed locations for a graph feed */
  export type GraphLocationProps = "left" | "right";

  export type SelectedFileItem = {
    is_checked: boolean;
    item_id: string;
    side: GraphLocationProps;
    name: string;
    meta: FeedMetaOut;
  }

  /** Represents a feed with its id and the location it should be displayed on */
  export type GraphFeedProps = { feed_id: number; location: GraphLocationProps };
  
  /** Contains data points and feed configurations for a line chart */
  export interface LineChartDataProps {
    data: GraphDataProps[];
    feeds: GraphFeedProps[];
  }
  
  /** Represents collections of vertical axis range values for different sides */
  export type VerticalRange = {
    left_top: number[];
    left_bottom: number[];
    right_top: number[];
    right_bottom: number[];
  };
  
  /** Basic zoom parameters for the graph */
  export type GraphZoom = {
    topLeft: string | number;
    bottomLeft: string | number;
    topRight: string | number;
    bottomRight: string | number;
    animation: boolean;
  };
  
  /**
   * Extended zoom state that includes additional properties.
   */
  export interface FullGraphZoom extends GraphZoom {
    /** Left axis minimum value indicator (or key) */
    left: string | number;
    /** Right axis maximum value indicator (or key) */
    right: string | number;
    /** Reference area start value for zooming */
    refAreaLeft: number;
    /** Reference area end value for zooming */
    refAreaRight: number;
  }