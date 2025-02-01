import clsx from 'clsx';
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import Ut from '@/utils/utils';
import { FeedMetaOut } from '@/emon-tools-api/dataViewerApi';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { ChangeEvent, ChangeEventHandler } from 'react';
import { SelectedFileItem } from '@/stores/dataViewerStore';

export interface IFilesData {
  feed_id: number,
  name: string,
  meta: FeedMetaOut
}

export interface IFiles {
    file_path: string,
    files: IFilesData[],
    invalid: string[],
    success: boolean
}
export type GraphSideYProps = ChangeEventHandler<HTMLInputElement>

type FilesListItemProps = {
  file_meta: {
    feed_id: number,
    name: string,
    meta: FeedMetaOut
  };
  handleSelectLeft: GraphSideYProps;
  handleSelectRight: GraphSideYProps;
  classBody?: string;
}

export function FilesListItem({
  file_meta,
  handleSelectLeft,
  handleSelectRight,
  classBody
}: FilesListItemProps) {

  return (
    <>
      <div
        className={clsx('w-full flex flex-col items-center gap-2 p-4 border-2 rounded-lg hover:border-white', classBody)}
      >
        <div
          className={clsx('w-full grid grid-cols-9 gap-2', classBody)}
        >
          <div className="col-span-3 text-sm flex items-center justify-center">
            <Input 
              type="checkbox"
              className='w-6 h-6 m-auto'
              value={file_meta.feed_id}
              onChange={handleSelectLeft}
            />
          </div>
          <div className="col-span-3 text-sm flex items-center justify-center border-x-2">
            <Button
              variant='outline'
              className='m-auto'
            >
              {file_meta.name}
            </Button>
          </div>
          <div className="col-span-3 text-sm flex items-center justify-center">
            <Input
              type="checkbox"
              className='w-6 h-6 m-auto'
              value={file_meta.feed_id}
              onChange={handleSelectRight}
            />
          </div>
        </div>
        <Separator className="my-2" />
        <div
          className={clsx('w-full grid grid-cols-12 gap-1', classBody)}
        >
          <div className="col-span-3 text-sm flex items-center justify-center">
            Start
          </div>
          <div className="col-span-3 text-sm flex items-center justify-center">
            End
          </div>
          <div className="col-span-3 text-sm flex items-center justify-center" title='Interval'>
            Interval
          </div>
          <div className="col-span-3 text-sm flex items-center justify-center">
            Size
          </div>
        </div>
        <div
          className={clsx('w-full grid grid-cols-12 gap-1', classBody)}
        >
          <div className="col-span-3 text-sm flex items-center justify-center">
            {Ut.toLocaleDateFromTime(file_meta.meta.start_time)}
          </div>
          <div className="col-span-3 text-sm flex items-center justify-center">
            {Ut.toLocaleDateFromTime(file_meta.meta.end_time)}
          </div>
          <div className="col-span-3 text-sm flex items-center justify-center" title='Interval'>
            {file_meta.meta.interval}
          </div>
          <div className="col-span-3 text-sm flex items-center justify-center">
            {Ut.formatBytes(file_meta.meta.npoints * 4, 3)}
          </div>
        </div>        
      </div>
      <Separator className="my-2" />
    </>
    
  )
}

type FilesListPaneProps = {
  data: IFiles;
  handleSelectItem: (item: SelectedFileItem) => void;
  classBody?: string;
}

export function FilesListPane({
    data,
    handleSelectItem,
    classBody
}: FilesListPaneProps) {
    const is_data = Ut.isObject(data) && data.success === true && Ut.isArray(data.files)

    const getSelectedFile = (e: ChangeEvent<HTMLInputElement>): SelectedFileItem =>{
      const target = e.target;
      const is_checked = target.type === 'checkbox' && target.checked;
      const item_id = parseInt(target.value)
      const selected_item = data.files.filter(item => item.feed_id === item_id)
      return{
        is_checked: is_checked,
        item_id: item_id.toString(),
        side: 'left',
        name: selected_item[0]?.name,
        meta: selected_item[0]?.meta
      }
    }

    const handleGraphLeft = (e: ChangeEvent<HTMLInputElement>) =>{
      const item = getSelectedFile(e);
      item.side = 'left'
      handleSelectItem(item)
    }

    const handleGraphRight = (e: ChangeEvent<HTMLInputElement>) =>{
      const item = getSelectedFile(e);
      item.side = 'right'
      handleSelectItem(item)
    }
    return (
        <ScrollArea
          className={clsx("h-72 w-full pt-20 rounded-md border", classBody)}
        >
          <div className="p-4">
            {
              is_data ? (
                data.files.map((file, index) => (
                  <FilesListItem
                    key={index}
                    file_meta={file}
                    handleSelectLeft={handleGraphLeft}
                    handleSelectRight={handleGraphRight} />
                ))
              ) : (
                <div>Unable to get files list</div>
              )
            }

          </div>
        </ScrollArea>
    )
}