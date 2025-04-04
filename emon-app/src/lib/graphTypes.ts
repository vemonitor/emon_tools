
  /**
   * Represents fina data and feed meta data type.
   */
  export type FeedMetaOut = {
    start_time: number,
    end_time: number,
    npoints: number,
    interval: number,
    size: number,
  }

  /**
   * Represents fina data and feed db item type.
   * From Emon-tools fastapi db.
   */
  export type FileDbOut = {
    file_id: number,
    name: string,
    slug: string,
    feed_id: number,
    emonhost_id: number,
  }

  export type RequestSource = "emoncms" | "files"

  export type DataViewerProps = {
    path_id: number
  }
  
  export interface GraphDataProps {
    date: number;
    [key: string]: number | null;
  }
  
  /** Allowed locations for a graph feed */
  export type GraphLocationProps = "left" | "right";

  export type GraphSource = "feeds" | "files";

  export interface FeedDb {
    id: number;
    userid: number,
    name: string,
    tag: string;
    public: boolean;
    engine: string;
    unit: string;
    meta: FeedMetaOut,
    files_db?: FileDbOut[]
  }
  
  export interface FeedListDb {
      success: boolean
      host_id: number
      nb_feeds: number
      feeds: FeedDb[]    
  }

  export type FinaFileDb = {
    file_name: string,
    name: string,
    meta: FeedMetaOut,
    file_db: {
      file_id: number,
      name: string,
      slug: string,
      feed_id: number,
      emonhost_id: number
    }
  };

  export type FinaFilesListDb = {
    success: boolean,
    path_id: number,
    nb_added: number,
    files: FinaFileDb[]
  };

  export type PreSelectedToGraph = {
    is_checked: boolean;
    id: number;
    side: GraphLocationProps;
  }

  export type SelectedToGraph = {
    is_checked: boolean;
    id: number;
    side: GraphLocationProps;
    name: string;
    meta: FeedMetaOut;
    file_db?: FileDbOut[];
  }

  export type SelectedFileItem = {
    type: "file";
    is_checked: boolean;
    file_name: string;
    side: GraphLocationProps;
    name: string;
    meta: FeedMetaOut;
    file_db?: FileDbOut;
  }

  export type SelectedEmonItem = {
    type: "feed";
    is_checked: boolean;
    id: number;
    side: GraphLocationProps;
    name: string;
    meta: FeedMetaOut;
    files_db?: FileDbOut[];
  }

  export type SelectedFeedItem = SelectedFileItem | SelectedEmonItem;

  export type timeSerie = [number, number | null | undefined, number | null | undefined, number | null | undefined]

  export type FinaDataIn = {
    success: boolean,
    file_id: number,
    feed_id: number,
    datapath_id: number,
    emonhost_id: number,
    file_name: string,
    name: string,
    data: timeSerie[],
  }

  export type FeedDataIn = {
    success: boolean,
    id: number,
    name: string,
    data: timeSerie[],
  }

  export type GraphDataIn = FinaDataIn | FeedDataIn

  /** Represents a feed with its id and the location it should be displayed on */
  export type GraphFeedProps = {
    id: number;
    name: string;
    location: GraphLocationProps;
    db_data?: {
      datapath_id: number;
      emonhost_id: number;
      feed_id: number;
    }[]
  };
  
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
  
  export type NavigationMenu = {
    can_reload: boolean,
    can_go_start: boolean;
    can_go_back: boolean;
    can_go_after: boolean;
    can_go_end: boolean;
    can_zoom_in: boolean;
    can_zoom_out: boolean;
    zoom_level: number;
    move_level: number;
  }
  
  export type GraphSelector = {
    left: string | number,
    right: string | number,
    refAreaLeft: number,
    refAreaRight: number
  }

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