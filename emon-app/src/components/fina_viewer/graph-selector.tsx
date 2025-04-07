import clsx from 'clsx';
import { ScrollArea } from "@/components/ui/scroll-area"
import Ut from '@/helpers/utils';
import { Input } from '@/components/ui/input';
import { ChangeEventHandler, PropsWithChildren } from 'react';
import { FeedMetaOut } from '@/lib/graphTypes';
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const SelectorItemVariants = cva(
    "w-full flex flex-col items-center gap-2 p-2 border-2 rounded-lg hover:border-white",
    {
        variants: {
            variant: {
                default:
                    "shadow hover:border-white",
                primary:
                    "shadow border-cyan-950 hover:border-white",
                success:
                    "shadow border-lime-950 hover:border-white",
                warning:
                    "shadow border-yellow-950 hover:border-white",
                error:
                    "shadow border-red-950 hover:border-white",
            },
        },
        defaultVariants: {
            variant: "default",
        },
    }
)

export interface ItemData {
    id: number,
    name: string,
    meta: FeedMetaOut,
    selected: boolean
}

export interface ItemsSelector {
    success: boolean
    category_id: number
    items: ItemData[]
}
type GraphSideYProps = ChangeEventHandler<HTMLInputElement>

type SelectorItemConainerProps = VariantProps<typeof SelectorItemVariants>
    & PropsWithChildren
    & {
        className?: string
    }

export function SelectorItemConainer({
    variant,
    children,
    className
}: SelectorItemConainerProps) {
    return (
        <div
            className={cn(
                'w-full flex flex-col items-center gap-2 p-2 border-2 rounded-lg hover:border-white',
                SelectorItemVariants({ variant, className }),
                
            )}
        >
            {children}
        </div>
    )
}

type SelectorItemHeaderProps = PropsWithChildren & {
    className?: string
}

export function SelectorItemHeader({
    children,
    className
}: SelectorItemHeaderProps) {
    return (
        <div
            className={cn('w-full flex items-center justify-center', className)}
        >
            {children}
        </div>
    )
}

type SelectorCheckProps = PropsWithChildren & {
    itemId: number;
    is_left: boolean;
    handleSelectLeft: GraphSideYProps;
    is_right: boolean;
    handleSelectRight: GraphSideYProps;
    className?: string
}

export function SelectorCheck({
    itemId,
    is_left,
    handleSelectLeft,
    is_right,
    handleSelectRight,
    children,
    className
}: SelectorCheckProps) {
    return (
        <div
            className={clsx('w-full grid grid-cols-9 gap-2', className)}
        >
            <div className="col-span-3 text-sm flex items-center justify-center">
                <Input
                    type="checkbox"
                    className='w-5 h-5 m-auto'
                    value={itemId}
                    onChange={handleSelectLeft}
                    checked={is_left}
                />
            </div>
            <div className="col-span-3 text-sm flex items-center justify-center border-x-2">
                {children}
            </div>
            <div className="col-span-3 text-sm flex items-center justify-center">
                <Input
                    type="checkbox"
                    className='w-5 h-5 m-auto'
                    value={itemId}
                    onChange={handleSelectRight}
                    checked={is_right}
                />
            </div>
        </div>
    )
}

type SelectorDetailProps = {
    meta: FeedMetaOut;
    className?: string
}

export function SelectorDetail({
    meta,
    className
}: SelectorDetailProps) {
    return (
        <div
            className={clsx('w-full', className)}
        >
            <div
                className={clsx('w-full grid grid-cols-12 gap-1')}
            >
                <div className="col-span-6 text-sm flex items-center justify-start">
                    Start
                </div>
                <div className="col-span-6 text-sm flex items-center justify-end">
                    End
                </div>
            </div>
            <div
                className={clsx('w-full grid grid-cols-12 gap-1')}
            >
                <div className="col-span-6 text-sm flex items-center justify-start">
                    {Ut.toLocaleDateFromTime(meta.start_time)}
                </div>
                <div className="col-span-6 text-sm flex items-center justify-end">
                    {Ut.toLocaleDateFromTime(meta.end_time)}
                </div>
                <div className="col-span-6 text-sm flex items-center justify-start" title='Interval'>
                    Interval: {meta.interval}
                </div>
                <div className="col-span-6 text-sm flex items-center justify-end">
                    Size: {Ut.formatBytes(meta.size)}
                </div>
            </div>
        </div> 
    )
}


type SelectorsPaneProps = PropsWithChildren & {
    className?: string
}

export function SelectorsPane({
    children,
    className
}: SelectorsPaneProps) {
    return (
        <ScrollArea
            className={cn('h-72 w-full pt-20 rounded-md border p-4', className)}
        >
            {children}
        </ScrollArea>
    )
}