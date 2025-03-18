import clsx from 'clsx';
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import Ut from '@/helpers/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ChangeEvent, ChangeEventHandler, useState } from 'react';
import { FeedMetaOut, FileDbOut, GraphLocationProps, SelectedFileItem } from '@/lib/graphTypes';
import { useDataViewer } from '@/stores/dataViewerStore';
import { BadgePlus, Pencil } from 'lucide-react';
import DialogForm from '@/components/form/dialog-form';
import EditArchiveFile from '@/routes/archive-file/edit';
import AddArchiveFile from '@/routes/archive-file/add';

export interface IFilesData {
  file_name: string,
  name: string,
  meta: FeedMetaOut,
  file_db?: FileDbOut
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
    file_name: string,
    name: string,
    meta: FeedMetaOut,
    file_db?: {
      file_id: number,
      name: string,
      slug: string,
      feed_id: number,
      emonhost_id: number,
    },
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
  const selected_feeds = useDataViewer((state) => state.selected_feeds)
  const [dialogOpen, dialogSetOpen] = useState(false);
  const is_selected = (side: GraphLocationProps) => {
    const selecteds = selected_feeds.filter(item=>item.side === side && item.file_name === file_meta.file_name)
    return selecteds.length > 0
  }

  const is_registered = Ut.isObject(file_meta.file_db) && Ut.isNumber(
    file_meta.file_db.file_id, {positive: true})
  
  const item_variant = is_registered ? 'border-lime-950' : 'border-red-950'
  
  const handleSuccessForm = () => {
    dialogSetOpen(false)
  }
  return (
    <>
      <div
        className={clsx(
          'w-full flex flex-col items-center gap-2 p-2 border-2 rounded-lg hover:border-white',
          classBody,
          item_variant
        )}
      >
        <div
          className={clsx('w-full flex items-center justify-center', classBody)}
        >
          {file_meta.name}
        </div>
        <Separator className="my-1" />
        <div
          className={clsx('w-full grid grid-cols-9 gap-2', classBody)}
        >
          <div className="col-span-3 text-sm flex items-center justify-center">
            <Input 
              type="checkbox"
              className='w-5 h-5 m-auto'
              value={file_meta.file_name}
              onChange={handleSelectLeft}
              checked={is_selected("left")}
            />
          </div>
          <div className="col-span-3 text-sm flex items-center justify-center border-x-2">
            {is_registered ? (
              <DialogForm
                dialogOpen={dialogOpen}
                dialogSetOpen={dialogSetOpen}
                title="Edit Fina File"
                trigger={(
                  <Button
                    variant='ghost'
                    className='m-auto'
                  >
                    Edit <Pencil />
                  </Button>
                )}
                form={(
                  <EditArchiveFile
                    row_id={file_meta.file_db?.file_id ?? undefined}
                    is_dialog={true}
                    successCallBack={handleSuccessForm}
                  />
                )}
              />
              
            ) : (
              <DialogForm
                dialogOpen={dialogOpen}
                dialogSetOpen={dialogSetOpen}
                title="Edit Fina File"
                trigger={(
                  <Button
                    variant='ghost'
                    className='m-auto'
                  >
                    Add <BadgePlus />
                  </Button>
                )}
                form={(
                  <AddArchiveFile
                    is_dialog={true}
                    successCallBack={handleSuccessForm}
                    data={{
                      file_name: file_meta.file_name,
                      name: file_meta.name,
                      start_time: file_meta.meta.start_time
                    }}
                  />
                )}
              />
              
            )}
          </div>
          <div className="col-span-3 text-sm flex items-center justify-center">
            <Input
              type="checkbox"
              className='w-5 h-5 m-auto'
              value={file_meta.file_name}
              onChange={handleSelectRight}
              checked={is_selected("right")}
            />
          </div>
        </div>
        <Separator className="my-1" />
        <div
          className={clsx('w-full grid grid-cols-12 gap-1', classBody)}
        >
          <div className="col-span-6 text-sm flex items-center justify-start">
            Start
          </div>
          <div className="col-span-6 text-sm flex items-center justify-end">
            End
          </div>
        </div>
        <div
          className={clsx('w-full grid grid-cols-12 gap-1', classBody)}
        >
          <div className="col-span-6 text-sm flex items-center justify-start">
            {Ut.toLocaleDateFromTime(file_meta.meta.start_time)}
          </div>
          <div className="col-span-6 text-sm flex items-center justify-end">
            {Ut.toLocaleDateFromTime(file_meta.meta.end_time)}
          </div>
          <div className="col-span-6 text-sm flex items-center justify-start" title='Interval'>
            Interval: {file_meta.meta.interval}
          </div>
          <div className="col-span-6 text-sm flex items-center justify-end">
            Size: {Ut.formatBytes(file_meta.meta.size)}
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
    
    const is_data = Ut.isObject(data) && Ut.isArray(data.files)

    const getSelectedFile = (e: ChangeEvent<HTMLInputElement>): SelectedFileItem =>{
      const target = e.target;
      const is_checked = target.type === 'checkbox' && target.checked;
      const file_name = target.value
      const selected_item = data.files.filter(item => item.file_name === file_name)
      return {
        is_checked: is_checked,
        file_name: file_name,
        side: 'left',
        name: selected_item[0]?.name,
        meta: selected_item[0]?.meta,
        file_db: selected_item[0]?.file_db
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
                    handleSelectRight={handleGraphRight}
                  />
                ))
              ) : (
                <div>Unable to get files list</div>
              )
            }

          </div>
        </ScrollArea>
    )
}