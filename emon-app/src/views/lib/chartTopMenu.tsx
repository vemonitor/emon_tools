import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Toggle } from '@/components/ui/toggle';
import { setZoom, useDataViewer } from '@/stores/dataViewerStore';
import { useQueryClient } from '@tanstack/react-query';
import clsx from 'clsx';
import { ArrowLeftFromLine, ArrowRightFromLine, BetweenHorizontalEnd, BetweenHorizontalStart, RotateCw, ZoomIn, ZoomOut } from 'lucide-react';
import { MouseEventHandler } from 'react';



type ChartTopMenuProps = {
  classBody?: string;
}

export function ChartTopMenu({
  classBody
}: ChartTopMenuProps) { //can_zoom_in
  const queryClient = useQueryClient();
  const go_back = useDataViewer((state) => state.go_back)
  const go_after = useDataViewer((state) => state.go_after)
  const zoom_in = useDataViewer((state) => state.zoom_in)
  const zoom_out = useDataViewer((state) => state.zoom_out)
  const can_zoom_in = useDataViewer((state) => state.can_zoom_in)
  const can_zoom_out = useDataViewer((state) => state.can_zoom_out)
  
  const handleGoBefore = (e: MouseEventHandler<HTMLButtonElement>) => {
    go_back()
    //queryClient.invalidateQueries({ queryKey: ['emon_fina_datas'] })
  }

  const handleGoAfter = (e: MouseEventHandler<HTMLButtonElement>) => {
    //e.preventDefault()
    go_after()
    //queryClient.invalidateQueries({ queryKey: ['emon_fina_datas'] })
  }
  const handleZoomIn = (e: MouseEventHandler<HTMLButtonElement>) => {
    //queryClient.cancelQueries({ queryKey: ['emon_fina_datas'] })
    zoom_in()  
  }
  const handleZoomOut = (e: MouseEventHandler<HTMLButtonElement>) => {
    //queryClient.cancelQueries({ queryKey: ['emon_fina_datas'] })
    zoom_out()
  }
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
        <Button
          variant={'ghost'}
        >
          <RotateCw />
        </Button>
        <Button
          onClick={handleZoomIn}
          disabled={!can_zoom_in}
          title='Zoom In'
          variant={'ghost'}
        >
          <ZoomIn />
        </Button>
        <Button
          onClick={handleZoomOut}
          disabled={!can_zoom_out}
          title='Zoom Out'
          variant={'ghost'}
        >
          <ZoomOut />
        </Button>
        <Button
          onClick={handleGoBefore}
          variant={'ghost'}
        >
          <ArrowLeftFromLine />
        </Button>
        <Button
          onClick={handleGoAfter}
          variant={'ghost'}
        >
          <ArrowRightFromLine />
        </Button>
        <Button
          onClick={handleGoBefore}
          variant={'ghost'}
        >
          <BetweenHorizontalStart />
        </Button>
        <Button
          onClick={handleGoAfter}
          variant={'ghost'}
        >
          <BetweenHorizontalEnd />
        </Button>
        
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
  const time_window = useDataViewer((state) => state.time_window)
  const set_time_window = useDataViewer((state) => state.set_time_window)

  const handleSelectChange = (value: string) => {
    set_time_window(parseInt(value))
  }

  return (
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
  )
}

export function GraphOptions({
  classBody
}: ChartTopMenuProps) {
  const connect_nulls = useDataViewer((state) => state.connect_nulls)
  const toggle_connect_nulls = useDataViewer((state) => state.toggle_connect_nulls)

  const handleConnectNulls = () => {
    toggle_connect_nulls()
  }

  return (
    <div className="flex flex-row gap-2 items-center">
      <Toggle
        id='show_missing_data'
        aria-label="Missing data"
        defaultPressed={connect_nulls}
        onPressedChange={handleConnectNulls}
      >Missing data</Toggle>
    </div>
  )
}