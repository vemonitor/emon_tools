import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from '@/components/ui/separator';
import { Toggle } from '@/components/ui/toggle';
import { setZoom, useDataViewer } from '@/stores/dataViewerStore';
import clsx from 'clsx';
import { ArrowLeftFromLine, ArrowLeftToLine, ArrowRightFromLine, ArrowRightToLine, ChartSpline, Eye, RotateCw, SearchCode, Unplug, ZoomIn, ZoomOut } from 'lucide-react';

type NavigationMenuProps = {
  can_go_back: boolean;
  handleGoBack: () => void;
  can_go_after: boolean;
  handleGoAfter: () => void;
  can_zoom_in: boolean;
  handleZoomIn: () => void;
  can_zoom_out: boolean;
  handleZoomOut: () => void
  can_go_start: boolean;
  handleGoStart: () => void
  can_go_end: boolean;
  handleGoEnd: () => void
  classBody?: string;
}

export function NavigationMenu({
  can_go_back,
  handleGoBack,
  can_go_after,
  handleGoAfter,
  can_zoom_in,
  handleZoomIn,
  can_zoom_out,
  handleZoomOut,
  can_go_start,
  handleGoStart,
  can_go_end,
  handleGoEnd,
  classBody
}: NavigationMenuProps) {
  
  return (
    <div className={clsx(
      "flex flex-row items-center",
      classBody
      )}>
      <Button
        variant={'ghost'}
      >
        <RotateCw />
      </Button>
      <Button
        onClick={()=>handleZoomIn()}
        disabled={!can_zoom_in}
        title='Zoom In'
        variant={'ghost'}
      >
        <ZoomIn />
      </Button>
      <Button
        onClick={()=>handleZoomOut()}
        disabled={!can_zoom_out}
        title='Zoom Out'
        variant={'ghost'}
      >
        <ZoomOut />
      </Button>
      <Button
        onClick={()=>handleGoStart()}
        disabled={!can_go_start}
        variant={'ghost'}
      >
        <ArrowLeftToLine />
      </Button>
      <Button
        onClick={()=>handleGoBack()}
        disabled={!can_go_back}
        variant={'ghost'}
      >
        <ArrowLeftFromLine />
      </Button>
      <Button
        onClick={()=>handleGoAfter()}
        disabled={!can_go_after}
        variant={'ghost'}
      >
        <ArrowRightFromLine />
      </Button>
      
      <Button
        onClick={()=>handleGoEnd()}
        disabled={!can_go_end}
        variant={'ghost'}
      >
        <ArrowRightToLine />
      </Button>
    </div>
  )
}

type NavMenuProps = {
  classBody?: string;
}

export function NavGraphMenu({
  classBody
}: NavMenuProps) {
  const nav_graph = useDataViewer((state) => state.nav_graph)

  const {
    go_back,
    go_after,
    zoom_in,
    zoom_out,
    go_start,
    go_end,
  } = useDataViewer()

  return (
    <NavigationMenu
        can_go_back={nav_graph.can_go_back}
        handleGoBack={go_back}
        can_go_after={nav_graph.can_go_after}
        handleGoAfter={go_after}
        can_zoom_in={nav_graph.can_zoom_in}
        handleZoomIn={zoom_in}
        can_zoom_out={nav_graph.can_zoom_out}
        handleZoomOut={zoom_out}
        can_go_start={nav_graph.can_go_start}
        handleGoStart={go_start}
        can_go_end={nav_graph.can_go_end}
        handleGoEnd={go_end}
        classBody={classBody}
      />
  )

}


export function NavViewMenu({
  classBody
}: NavMenuProps) {
  const nav_view = useDataViewer((state) => state.nav_view)

  const {
    go_back,
    go_after,
    zoom_in,
    zoom_out,
    go_start,
    go_end,
  } = useDataViewer()

  return (
    <NavigationMenu
        can_go_back={nav_view.can_go_back}
        handleGoBack={go_back}
        can_go_after={nav_view.can_go_after}
        handleGoAfter={go_after}
        can_zoom_in={nav_view.can_zoom_in}
        handleZoomIn={zoom_in}
        can_zoom_out={nav_view.can_zoom_out}
        handleZoomOut={zoom_out}
        can_go_start={nav_view.can_go_start}
        handleGoStart={go_start}
        can_go_end={nav_view.can_go_end}
        handleGoEnd={go_end}
        classBody={classBody}
      />
  )

}

type ChartTopMenuProps = {
  classBody?: string;
}

export function ChartTopMenu({
  classBody
}: ChartTopMenuProps) { //can_zoom_in
  const can_zoom_view = useDataViewer((state) => state.can_zoom_view)
  const toggle_can_zoom_view = useDataViewer((state) => state.toggle_can_zoom_view)

  return (
  <div
    className={clsx(
      'w-full flex flex-col items-start gap-2 px-4 h-10',
      classBody
    )}
  >
    <div
      className={clsx(
        'w-full flex flex-row items-center justify-between gap-2 h-10',
        classBody
      )}
    >
      <div className="flex flex-row items-center">
        <Toggle
          id='zoom_graph_status'
          aria-label="Graph/View Zoom Status" 
          defaultPressed={can_zoom_view}
          onPressedChange={()=>toggle_can_zoom_view()}
        >Nav : {can_zoom_view === true ? <Eye /> : <ChartSpline />}</Toggle>
        <Separator orientation='vertical' decorative={true} className='w-1'></Separator>
        <NavGraphMenu
        />
      </div>
      <div className="">
        <GraphOptions />
      </div>
      <div className="">
        <ZoomSelector />
      </div>
    </div>
    
  </div>

  )
}

export function ZoomSelector({
  classBody
}: ChartTopMenuProps) {
  const interval = useDataViewer((state) => state.interval)
  const time_window = useDataViewer((state) => state.time_window)
  const set_time_window = useDataViewer((state) => state.set_time_window)

  const handleSelectChange = (value: string) => {
    set_time_window(parseInt(value))
  }

  return (
    <div className="flex flex-row items-center">
      <Input
        type="number"
        readOnly={true}
        value={interval}
        maxLength={8}
        size={8}
        className='w-20'
      >
      </Input>
      <Select
        value={setZoom.get_zoom_by_window(time_window).time_window.toString()}
        onValueChange={handleSelectChange}
      >
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Select zoom" />
        </SelectTrigger>
        <SelectContent className={classBody}>
          <SelectGroup>
            <SelectLabel>Zoom</SelectLabel>
            {setZoom.get_static_zooms()
              .filter(val => val.time_window >= 1800 && val.time_window <= 62899200)
              .map((val, index) => {
                return (<SelectItem key={index} value={val.time_window.toString()}>{val.label}</SelectItem>)
              })
            }
          </SelectGroup>
        </SelectContent>
      </Select>
    </div>
  )
}

export function GraphOptions({
  classBody
}: ChartTopMenuProps) {
  const connect_nulls = useDataViewer((state) => state.connect_nulls)
  const toggle_connect_nulls = useDataViewer((state) => state.toggle_connect_nulls)

  return (
    <div
      className={clsx(
        "flex flex-row gap-2 items-center",
        classBody)}
    >
      <Toggle
        id='show_missing_data'
        aria-label="Missing data"
        defaultPressed={connect_nulls}
        onPressedChange={()=>toggle_connect_nulls()}
      ><Unplug />Missing data</Toggle>
    </div>
  )
}